import React from 'react';
import { motion } from 'framer-motion';
import { Upload, Zap } from 'lucide-react';
import { Button } from '../ui/button';
import { MagneticWrapper } from '../ui/MagneticWrapper';

interface UploadZoneProps {
  file: File | null;
  isProcessing: boolean;
  progress: number;
  onDragOver: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  onUploadClick: () => void;
  onProcess: () => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  file,
  isProcessing,
  progress,
  onDragOver,
  onDrop,
  onUploadClick,
  onProcess
}) => {
  return (
    <div
      onDragOver={onDragOver}
      onDrop={onDrop}
      className={`
        group relative cursor-pointer
        border border-white/10 hover:border-neon-purple/50
        bg-white/5 hover:bg-white/[0.07] backdrop-blur-2xl
        rounded-3xl p-16 transition-all duration-500
        overflow-hidden
        ${isProcessing ? 'pointer-events-none' : ''}
      `}
      onClick={onUploadClick}
    >
      {/* Glowing border effect */}
      <div className="absolute inset-0 bg-gradient-to-b from-neon-purple/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="relative z-10 flex flex-col items-center gap-6">
        <div className="relative">
          <div className="absolute inset-0 bg-neon-purple/30 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          <div className="h-20 w-20 bg-black/50 border border-white/20 rounded-2xl flex items-center justify-center relative shadow-2xl group-hover:scale-110 transition-transform duration-300">
            {isProcessing ? (
              <div className="w-10 h-10 border-4 border-neon-purple border-t-transparent rounded-full animate-spin" />
            ) : (
              <Upload className="w-10 h-10 text-white group-hover:text-neon-cyan transition-colors duration-300" />
            )}
          </div>
        </div>

        <div className="space-y-2 text-center">
          <h3 className="text-2xl font-bold text-white">
            {isProcessing ? 'Transcribing Audio...' : file ? file.name : 'Drop Audio Here'}
          </h3>
          {!isProcessing && !file && (
            <p className="text-gray-400 font-mono text-sm">
              Supports MP3, WAV, M4A, FLAC
            </p>
          )}
          
          {isProcessing && (
             <div className="w-64 h-1 bg-white/10 rounded-full mt-4 overflow-hidden mx-auto">
               <motion.div 
                 className="h-full bg-neon-gradient"
                 style={{ width: `${progress}%` }}
               />
             </div>
          )}
        </div>

        {file && !isProcessing && (
          <MagneticWrapper className="mt-4">
            <Button
              size="lg"
              onClick={(e) => { e.stopPropagation(); onProcess(); }}
              className="bg-white text-black hover:bg-neon-cyan hover:text-black font-bold text-lg px-10 h-14 rounded-full shadow-[0_0_20px_rgba(255,255,255,0.3)] hover:shadow-[0_0_40px_rgba(0,240,255,0.5)] transition-all duration-300"
            >
               <Zap className="w-5 h-5 mr-2 fill-black" />
               Start Magic
            </Button>
          </MagneticWrapper>
        )}
      </div>
    </div>
  );
};
