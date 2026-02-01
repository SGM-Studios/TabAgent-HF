import { useState, useEffect } from 'react';
import { HeroBackground } from './components/ui/HeroBackground';
import { Navbar } from './components/layout/Navbar';
import { UploadZone } from './components/features/UploadZone';
import { ResultsDashboard } from './components/features/ResultsDashboard';
import { Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Client } from "@gradio/client";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [progress, setProgress] = useState(0);

  const [tabContent, setTabContent] = useState<string>("");
  const [downloadUrl, setDownloadUrl] = useState<string>("");
  const [statusMsg, setStatusMsg] = useState<string>("");

  // Simulated progress for viral effect
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isProcessing) {
      setProgress(0);
      interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 95) return prev;
          return prev + Math.random() * 5;
        });
      }, 200);
    } else {
      setProgress(0);
    }
    return () => clearInterval(interval);
  }, [isProcessing]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUploadClick = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'audio/*';
    input.onchange = (e) => {
      const target = e.target as HTMLInputElement;
      if (target.files && target.files[0]) {
        setFile(target.files[0]);
      }
    };
    input.click();
  };

  const handleProcess = async () => {
    if (!file) return;
    setIsProcessing(true);

    try {
      if (!import.meta.env.VITE_HF_TOKEN) {
        throw new Error("Missing VITE_HF_TOKEN. Please restart your dev server to load the .env file.");
      }

      // Initialize the client
      const client = await Client.connect("scottymills/tab-agent-pro", {
        // @ts-expect-error - hf_token is valid at runtime
        hf_token: import.meta.env.VITE_HF_TOKEN
      });

      // Use the predict API
      const result = await client.predict("/process_audio", {
        audio_file: file,
        instrument: "Guitar",
        tuning: "Guitar (Standard)",
        include_midi: true,
        include_tab: true,
        include_json: true,
        detect_suno: true
      });
      
      console.log("Result:", result);
      
      // Store results
      if (result.data) {
          const [status, zipFile, tabText] = result.data as [string, any, string];
          setStatusMsg(status);
          setTabContent(tabText);
          if (zipFile?.url) {
              setDownloadUrl(zipFile.url);
          }
      }

      setIsComplete(true);
    } catch (error: unknown) {
      console.error("Transcription failed:", error);
      alert("Transcription failed. See console for details.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setIsComplete(false);
    setFile(null);
    setTabContent("");
    setDownloadUrl("");
    setStatusMsg("");
  };

  return (
    <div className="min-h-screen font-sans text-white bg-black overflow-x-hidden selection:bg-neon-purple/30">
      <HeroBackground />
      
      {/* Noise Overlay */}
      <div className="noise-bg pointer-events-none fixed inset-0 z-[100] opacity-[0.03]" />

      <Navbar />

      {/* Main Content */}
      <main className="pt-32 pb-20 px-6 relative z-10">
        <div className="max-w-5xl mx-auto">
          
          <div className="text-center space-y-8 mb-20">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-4"
            >
              <Sparkles className="w-4 h-4 text-neon-purple animate-pulse" />
              <span className="text-xs font-mono text-gray-300">POWERED BY ZERO GPU</span>
            </motion.div>

            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="font-display text-6xl md:text-8xl font-bold tracking-tighter leading-tight text-white"
            >
              <span className="bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-gray-500">
                Audio to Tab.
              </span>
              <br />
              <span className="bg-clip-text text-transparent bg-neon-gradient relative inline-block">
                Instantly.
                <motion.svg
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 1.5, delay: 1 }}
                  className="absolute -bottom-4 left-0 w-full h-4 text-neon-cyan"
                  viewBox="0 0 100 10"
                  preserveAspectRatio="none"
                >
                  <motion.path
                    d="M0 5 Q 50 10 100 5"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  />
                </motion.svg>
              </span>
            </motion.h1>

            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="text-lg text-gray-400 max-w-xl mx-auto"
            >
              The world's first AI transcriber that actually works. 
              Drop any audio file to generate professional Guitar & Bass tabs in seconds.
            </motion.p>
          </div>

          <AnimatePresence mode="wait">
            {!isComplete ? (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
                transition={{ duration: 0.5 }}
                className="max-w-2xl mx-auto"
              >
               <UploadZone 
                 file={file}
                 isProcessing={isProcessing}
                 progress={progress}
                 onDragOver={handleDragOver}
                 onDrop={handleDrop}
                 onUploadClick={handleUploadClick}
                 onProcess={handleProcess}
               />
              </motion.div>
            ) : (
              <motion.div
                key="results"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full"
              >
                <ResultsDashboard 
                  tabContent={tabContent}
                  downloadUrl={downloadUrl}
                  statusMsg={statusMsg}
                  onReset={handleReset}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

export default App;
