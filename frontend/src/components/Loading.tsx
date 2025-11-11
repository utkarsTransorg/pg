import { motion } from "framer-motion";
import { Loader2, CheckCircle } from "lucide-react";
import { useEffect, useState } from "react";

export default function Loading({ completed }: { completed?: boolean }) {
  // Gradually increase progress while not completed

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30 backdrop-blur-sm">
      <div className="flex flex-col items-center justify-center h-screen w-full bg-gradient-to-b from-[#0f172a] to-[#1e293b] text-white">
        {!completed ? (
          <>
            {/* Rotating loader */}
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
              className="mb-6"
            >
              <Loader2 size={60} className="text-blue-400 drop-shadow-md" />
            </motion.div>

            {/* Typing / Step Text */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-lg text-blue-200 font-medium"
            >
              {"loading..."}
            </motion.div>

            <p className="mt-4 text-xs text-blue-400/70 animate-pulse">
              Agent is working...
            </p>
          </>
        ) : (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.6 }}
            className="flex flex-col items-center gap-3"
          >
            <CheckCircle className="text-green-400" size={60} />
            <h2 className="text-xl font-semibold">Documentation Generated!</h2>
            <p className="text-blue-200 text-sm">Redirecting to overview...</p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
