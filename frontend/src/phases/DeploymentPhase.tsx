import React, { useState, useEffect } from "react";

const fakeLogs = [
  "[INFO] Starting deployment process...",
  "[BUILD] Compiling application...",
  "[BUILD] Transpiling React components...",
  "[BUILD] Optimizing assets...",
  "[SUCCESS] Build completed successfully.",
  "[UPLOAD] Connecting to hosting server...",
  "[UPLOAD] Uploading files...",
  "[UPLOAD] Verifying upload integrity...",
  "[CONFIG] Applying environment variables...",
  "[VERIFY] Running post-deployment checks...",
  "[SUCCESS] Application deployed successfully 🎉",
  "[INFO] Access your app at: https://aksl-gldf-sncn.transorg.com",
];

const DeploymentPage = () => {
  const [logs, setLogs] = useState([]);
  const [deploying, setDeploying] = useState(false);
  const [index, setIndex] = useState(0);

  const [showPrompt, setShowPrompt] = useState(false);
  const [promptAccepted, setPromptAccepted] = useState(false);

  // feedback states
  const [feedbackVisible, setFeedbackVisible] = useState(false);
  const [feedbackChoice, setFeedbackChoice] = useState("");
  const [feedbackText, setFeedbackText] = useState("");
  const [submitted, setSubmitted] = useState(false);

  // Start the initial fake check before deployment
  const startPreDeployment = () => {
    setShowPrompt(true);
  };

  const handlePromptResponse = (accept) => {
    setShowPrompt(false);
    if (accept) {
      setPromptAccepted(true);
      startFakeDeployment();
    } else {
      setLogs([
        "[INFO] Deployment cancelled by user.",
        "[INFO] You can deploy again anytime!",
      ]);
    }
  };

  const startFakeDeployment = () => {
    setLogs([]);
    setDeploying(true);
    setIndex(0);
    setFeedbackVisible(false);
    setFeedbackChoice("");
    setFeedbackText("");
    setSubmitted(false);
  };

  useEffect(() => {
    if (deploying && index < fakeLogs.length) {
      const timeout = setTimeout(() => {
        setLogs((prev) => [...prev, fakeLogs[index]]);
        setIndex((prev) => prev + 1);
      }, 1800);
      return () => clearTimeout(timeout);
    } else if (index >= fakeLogs.length && deploying) {
      setDeploying(false);
      setTimeout(() => setFeedbackVisible(true), 1000);
    }
  }, [deploying, index]);

  const handleFeedbackSubmit = () => {
    setSubmitted(true);
    setTimeout(() => setFeedbackVisible(false), 2000);
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-white font-sans p-10">
      <main className="p-8">
        <h2 className="text-xl font-bold mb-2">Deployment</h2>
        <p className="text-gray-400 mb-6">
          Click <span className="font-semibold text-blue-400">Deploy</span> to
          start the deployment process for your generated web app.
        </p>

        {/* Deploy Button */}
        <button
          onClick={startPreDeployment}
          disabled={deploying || showPrompt}
          className={`px-6 py-2 rounded-lg text-lg font-semibold transition ${
            deploying || showPrompt
              ? "bg-gray-600 cursor-not-allowed"
              : "bg-[#2F4F81] hover:bg-[#2F4F81]"
          }`}
        >
          {deploying ? "Deploying..." : "Deploy"}
        </button>

        {/* Fake Instance Prompt */}
        {showPrompt && (
          <div className="mt-6 p-4 bg-[#1e293b] border border-gray-600 rounded-lg shadow-lg">
            <p className="text-gray-200 mb-3">
              Detected an available compute instance inst-us-east-02.
              Configuration: 2 vCPUs, 4 GB RAM, Ubuntu 22.04 LTS. Proceed with
              deployment
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => handlePromptResponse(true)}
                className="bg-green-600 hover:bg-green-700 px-4 py-1 rounded-lg"
              >
                Yes, Deploy
              </button>
              <button
                onClick={() => handlePromptResponse(false)}
                className="bg-red-600 hover:bg-red-700 px-4 py-1 rounded-lg"
              >
                No, Cancel
              </button>
            </div>
          </div>
        )}

        {/* Logs Box */}
        <div className="mt-8 bg-black border border-gray-700 rounded-xl p-4 font-mono text-sm h-96 overflow-y-auto shadow-inner">
          {logs.length === 0 && !deploying && !showPrompt ? (
            <p className="text-gray-500 italic">
              Logs will appear here after deployment starts...
            </p>
          ) : (
            logs.map((line, i) => (
              <p
                key={i}
                className={`${
                  line.includes("SUCCESS")
                    ? "text-green-400"
                    : line.includes("ERROR")
                    ? "text-red-400"
                    : "text-gray-300"
                }`}
              >
                {line}
              </p>
            ))
          )}
        </div>

        {/* Status */}
        {logs.length > 0 && !deploying && !showPrompt && promptAccepted && (
          <div className="mt-4 p-3 bg-green-900/40 border border-green-600 rounded-lg">
            Deployment completed successfully!
          </div>
        )}

        {/* Feedback Section */}
        {feedbackVisible && !submitted && (
          <div className="mt-6 p-5 bg-[#1e293b] border border-gray-700 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">
              How was your deployment experience?
            </h3>
            <div className="flex gap-3 mb-3">
              {["Smooth", "Needs Improvement", "Failed "].map((opt) => (
                <button
                  key={opt}
                  onClick={() => setFeedbackChoice(opt)}
                  className={`px-3 py-1 rounded-md border ${
                    feedbackChoice === opt
                      ? "bg-blue-700 border-blue-400"
                      : "border-gray-600 hover:border-blue-400"
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>

            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="Share any thoughts or suggestions..."
              className="w-full bg-[#0f172a] border border-gray-700 rounded-lg p-2 text-gray-200 text-sm resize-none h-24 mb-3"
            />
            <button
              onClick={handleFeedbackSubmit}
              disabled={!feedbackChoice && feedbackText.trim() === ""}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-1 rounded-lg"
            >
              Submit Feedback
            </button>
          </div>
        )}

        {submitted && (
          <div className="mt-4 p-3 bg-green-900/40 border border-green-600 rounded-lg">
            Thanks for your feedback!
          </div>
        )}
      </main>
    </div>
  );
};

export default DeploymentPage;
