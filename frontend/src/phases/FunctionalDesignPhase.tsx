import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { BACKEND_URL } from "../../config";
import { Download } from "lucide-react";
import { marked } from "marked";
import Loading from "../components/Loading";
import ToastError from "../components/ToastError";

export default function FunctionalDesignPhase() {
  const location = useLocation();
  const data = location.state?.data;
  const [functionalDocument, setFunctionalDocument] = useState<string>("");
  const [loading, setLoading] = useState(false);
  console.log(functionalDocument);

  // 🧹 --- Markdown Cleaner Function ---
  const normalizeMarkdown = (rawDoc: string): string => {
    if (!rawDoc) return "";

    let md = rawDoc;

    // 1️⃣ Decode escaped newlines
    md = md.replace(/\\n/g, "\n");

    // 2️⃣ Remove any markdown code fences like ``` or ```markdown
    md = md.replace(/```(?:markdown)?/gi, "");

    // 3️⃣ Remove any super long Markdown tables (corrupted ones)
    md = md.replace(/\n\|[\s\S]*?(?=\n###|\n##|\Z)/g, "\n\n");

    // 4️⃣ Remove any leftover HTML tags
    md = md.replace(/<[^>]+>/g, "");

    // 5️⃣ Clean multiple spaces/tabs/newlines
    md = md.replace(/\t+/g, " ");
    md = md.replace(/ {2,}/g, " ");
    md = md.replace(/\n{3,}/g, "\n\n");

    // 6️⃣ Normalize section headings
    md = md.replace(/###\s*\d+\.\s*/g, "### ");
    md = md.replace(/##\s*\d+\.\s*/g, "## ");

    // 7️⃣ Remove duplicate "FUNCTIONAL REQUIREMENTS" remnants
    md = md.replace(
      /### FUNCTIONAL REQUIREMENTS\s*### FUNCTIONAL REQUIREMENTS/g,
      "### FUNCTIONAL REQUIREMENTS"
    );

    // 8️⃣ Ensure spacing before/after each heading
    md = md.replace(/(### [^\n]+)/g, "\n\n$1\n\n");

    // 9️⃣ Trim extra whitespace at start and end
    return md.trim();
  };

  // 🧾 Fetch Functional Design Phase Document
  const getFunctionalDesignPhaseDoc = async () => {
    setLoading(true);
    try {
      if (location.state?.["functional-design"]?.document) {
        console.log("yes");
        setFunctionalDocument(location.state["functional-design"].document);
        return;
      }

      if (!data?.session_id) throw new Error("Session ID is missing");

      const payload = { session_id: data.session_id, feedback: "approved" };
      console.log("hii");
      const response = await fetch(
        `${BACKEND_URL}/documents/functional/generate/${data.session_id}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok)
        throw new Error(
          "Failed to call /documents/functional/generate/{{session_id}}"
        );

      const functional_doc = await response.json();
      setFunctionalDocument(functional_doc?.document || "");
    } catch (error) {
      console.error(
        "error calling /documents/functional/generate/{{session_id}}"
      );
      ToastError(error);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (data) getFunctionalDesignPhaseDoc();
  }, [location.state]);

  const generateMarkdown = (): string => normalizeMarkdown(functionalDocument);

  // 💾 Download as Word (.doc)
  const handleDownload = () => {
    const markdownContent = generateMarkdown();
    const htmlConverted = marked(markdownContent);

    const htmlContent = `
      <html xmlns:o='urn:schemas-microsoft-com:office:office'
            xmlns:w='urn:schemas-microsoft-com:office:word'
            xmlns='http://www.w3.org/TR/REC-html40'>
        <head>
          <meta charset='utf-8'>
          <title>Functional Design Phase Document</title>
          <style>
            body { font-family: 'Arial', sans-serif; margin: 20px; color: #374151; }
            h1 { font-size: 24px; color: #1e40af; font-weight: bold; margin: 20px 0 10px; }
            h2 { font-size: 20px; color: #1e3a8a; font-weight: 600; margin: 18px 0 8px; }
            h3 { font-size: 18px; color: #1e3a8a; margin: 16px 0 6px; }
            p { font-size: 14px; line-height: 1.6; margin: 8px 0; }
            ul { margin-left: 20px; }
            pre { background: #f3f4f6; padding: 10px; border-radius: 4px; }
          </style>
        </head>
        <body>${htmlConverted}</body>
      </html>`;

    const blob = new Blob([htmlContent], { type: "application/msword" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const title = data?.project_requirements?.title || "FunctionalDesignPhase";
    link.href = url;
    link.download = `${title}_functional_doc.doc`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (loading) return <Loading currentStep={2} />;

  return (
    <div className="flex-1 p-6 overflow-y-auto bg-gray-90 bg-gray-900">
      <div className="max-w-6xl mx-auto">
        <div className="bg-gray-800 rounded-lg shadow-xl p-8 border border-gray-700">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-3xl font-bold text-white">
              Functional Design Phase Document
            </h1>
            <button
              onClick={handleDownload}
              className="bg-green-600 hover:bg-green-700 text-green-200 font-bold py-2 px-4 
                         flex gap-2 items-center justify-center rounded-full text-sm 
                         active:scale-[.9] hover:scale-[1.02]"
            >
              <Download className="h-4 w-4 font-bold animate-bounce" /> Download
            </button>
          </div>

          <div
            className="
              prose prose-invert 
              max-w-none
              prose-h1:text-xl prose-h1:mt-4 prose-h1:mb-2
              prose-h2:text-lg prose-h2:mt-3 prose-h2:mb-2
              prose-h3:text-base prose-h3:mt-2 prose-h3:mb-1
              prose-p:my-2 
              prose-hr:my-4
              prose-headings:font-semibold prose-headings:text-blue-400 
              prose-strong:text-white
            "
          >
            <ReactMarkdown>{generateMarkdown()}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}
