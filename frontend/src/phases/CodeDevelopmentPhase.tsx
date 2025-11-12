import { useEffect, useState } from "react";
import axios from "axios";
import { BACKEND_URL } from "../../config";
import { FileExplorer } from "../components/FileExplorer";
import { FilePreview } from "../components/FilePreview";
import { useInitializeProject } from "../hooks/useInitializeProject";
import { useLocation } from "react-router-dom";
import { parseXml } from "../utils";
import { FileItem, Step, StepType } from "../types";
import { TabView } from "../components/TabView";
import { useWebContainer } from "../hooks/useWebContainer";
import { PreviewFrame } from "../components/PreviewFrame";
import Loading from "../components/Loading";
import ToastError from "../components/ToastError";
import { Upload } from "lucide-react";

interface BuilderProps {
  selectedPhase: string;
  files: FileItem[];
  setFiles: (files: FileItem[]) => void;
}

export function CodeDevelopmentPhase({
  selectedPhase,
  files,
  setFiles,
}: BuilderProps) {
  useInitializeProject();

  const location = useLocation();
  const webContainer = useWebContainer();
  const { task } = location.state as { task: string };
  const data = location.state?.data;
  const [loading, setLoading] = useState(false);

  const [steps, setSteps] = useState<Step[]>([]);
  const [llmMessages, setLlmMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([]);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [activeTab, setActiveTab] = useState<"code" | "preview">("code");

  // Popup state for snippet upload
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [snippetContent, setSnippetContent] = useState("");

  useEffect(() => {
    const createMountStructure = (files: FileItem[]): Record<string, any> => {
      const mountStructure: Record<string, any> = {};
      const processFile = (file: FileItem, isRootFolder: boolean) => {
        if (file.type === "folder") {
          mountStructure[file.name] = {
            directory: file.children
              ? Object.fromEntries(
                  file.children.map((child) => [
                    child.name,
                    processFile(child, false),
                  ])
                )
              : {},
          };
        } else if (file.type === "file") {
          if (isRootFolder) {
            mountStructure[file.name] = {
              file: { contents: file.content || "" },
            };
          } else {
            return { file: { contents: file.content || "" } };
          }
        }
        return mountStructure[file.name];
      };
      files.forEach((file) => processFile(file, true));
      return mountStructure;
    };

    const mountStructure = createMountStructure(files);
    webContainer?.mount(mountStructure);
  }, [files, webContainer]);

  useEffect(() => {
    let originalFiles = [...files];
    let updateHappened = false;
    steps
      .filter(({ status }) => status === "pending")
      .map((step) => {
        updateHappened = true;
        if (step?.type === StepType.CreateFile) {
          let parsedPath = step.path?.split("/") ?? [];
          let currentFileStructure = [...originalFiles];
          const finalAnswerRef = currentFileStructure;
          let currentFolder = "";

          while (parsedPath.length) {
            currentFolder = `${currentFolder}/${parsedPath[0]}`;
            const currentFolderName = parsedPath[0];
            parsedPath = parsedPath.slice(1);

            if (!parsedPath.length) {
              const file = currentFileStructure.find(
                (x) => x.path === currentFolder
              );
              if (!file) {
                currentFileStructure.push({
                  name: currentFolderName,
                  type: "file",
                  path: currentFolder,
                  content: step.code,
                });
              } else {
                file.content = step.code;
              }
            } else {
              const folder = currentFileStructure.find(
                (x) => x.path === currentFolder
              );
              if (!folder) {
                currentFileStructure.push({
                  name: currentFolderName,
                  type: "folder",
                  path: currentFolder,
                  children: [],
                });
              }
              currentFileStructure = currentFileStructure.find(
                (x) => x.path === currentFolder
              )!.children!;
            }
          }
          originalFiles = finalAnswerRef;
        }
      });

    if (updateHappened) {
      setFiles(originalFiles);
      setSteps((steps) =>
        steps.map((s: Step) => ({ ...s, status: "completed" }))
      );
    }
  }, [steps, files]);

  async function init() {
    setLoading(true);
    if (data) {
      try {
        let stepsToSet: Step[] = [];
        let messagesToSet = [{ role: "user", content: task } as const];

        if (selectedPhase === "frontend-coding") {
          let frontendResponse;
          if (location.state?.["frontend-coding"]?.code) {
            frontendResponse = location.state?.["frontend-coding"]?.code;
          } else {
            const response = await axios.post(
              `${BACKEND_URL}/code/frontend/generate/${data.session_id}`,
              { prompt: task }
            );
            frontendResponse = response.data.code;
          }
          const frontendSteps = parseXml(frontendResponse).map((x) => ({
            ...x,
            status: "pending" as const,
            code_type: "frontend",
          }));
          stepsToSet = frontendSteps;
          messagesToSet.push({ role: "assistant", content: frontendResponse });
        }

        if (selectedPhase === "backend-coding") {
          let backendResponse;
          if (location.state?.["backend-coding"]?.code) {
            backendResponse = location.state?.["backend-coding"]?.code;
          } else {
            const response = await axios.post(
              `${BACKEND_URL}/code/backend/generate/${data.session_id}`,
              { prompt: task }
            );
            backendResponse = response.data.code;
          }
          const backendSteps = parseXml(backendResponse).map((x) => ({
            ...x,
            status: "pending" as const,
            code_type: "backend",
          }));
          stepsToSet = backendSteps;
          messagesToSet.push({ role: "assistant", content: backendResponse });
        }

        setSteps(stepsToSet);
        setLlmMessages(messagesToSet);
        setLoading(false);
      } catch (error: any) {
        console.error("Error during code generation", error);
        setLoading(false);
        ToastError(error);
      }
    }
  }

  useEffect(() => {
    init();
  }, [selectedPhase, location.state]);

  // 🧠 Debug Upload: File
  const handleDebugUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      setFiles((prev) => [
        ...prev,
        {
          name: file.name,
          type: "file",
          path: `/${file.name}`,
          content: text,
        },
      ]);
      setSelectedFile({
        name: file.name,
        type: "file",
        path: `/${file.name}`,
        content: text,
      });
      ToastError("Debug file loaded successfully!");
    } catch {
      ToastError("Failed to load debug file");
    }
  };

  // 🧠 Debug Upload: Snippet
  const handleSnippetSave = () => {
    if (!snippetContent.trim()) {
      ToastError("Snippet is empty");
      return;
    }
    const fileName = `debug-snippet-${Date.now()}.ts`;
    const fileItem: FileItem = {
      name: fileName,
      type: "file",
      path: `/${fileName}`,
      content: snippetContent,
    };
    setFiles((prev) => [...prev, fileItem]);
    setSelectedFile(fileItem);
    setIsModalOpen(false);
    setSnippetContent("");
    ToastError("Snippet added successfully!");
  };

  if (loading) return <Loading />;

  return (
    <div className="flex-1 overflow-hidden">
      <div className="h-full grid grid-cols-3 gap-6 p-6">
        {/* LEFT PANEL */}
        <div className="col-span-1 flex flex-col space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-300">
              Project Files
            </h2>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsModalOpen(true)}
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-sm text-white rounded-lg"
              >
                Debug
              </button>
            </div>
          </div>

          <FileExplorer files={files} onFileSelect={setSelectedFile} />
        </div>

        {/* RIGHT PANEL */}
        <div className="col-span-2 bg-gray-900 rounded-lg shadow-lg h-[calc(100vh-8rem)]">
          <TabView
            selectedPhase={selectedPhase}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
          <div className="h-[calc(100%-4rem)]">
            {activeTab === "code" ? (
              <FilePreview selectedFile={selectedFile} />
            ) : (
              <PreviewFrame webContainer={webContainer} />
            )}
          </div>
        </div>
      </div>

      {/* 🧩 MODAL FOR SNIPPET INPUT */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50">
          <div className="bg-gray-800 p-6 rounded-xl w-[600px] shadow-lg border border-gray-700">
            <h2 className="text-lg font-semibold text-gray-200 mb-4">
              Paste Your Code Snippet
            </h2>
            <textarea
              className="w-full h-60 bg-gray-900 text-gray-100 p-3 rounded-md border border-gray-700 resize-none"
              placeholder="Paste your code snippet here..."
              value={snippetContent}
              onChange={(e) => setSnippetContent(e.target.value)}
            />
            <div className="flex justify-end mt-4 gap-3">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleSnippetSave}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white"
              >
                Add Snippet
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
