import React from 'react';
import { motion } from 'framer-motion';
import { Share2, Download, CheckCircle } from 'lucide-react';
import { Button } from '../ui/button';

interface ResultsDashboardProps {
  tabContent: string;
  downloadUrl: string;
  statusMsg: string;
  onReset: () => void;
}

export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({
  tabContent,
  downloadUrl,
  statusMsg,
  onReset
}) => {
  return (
    <div className="grid md:grid-cols-12 gap-6">
      {/* Result Card */}
      <div className="md:col-span-8 space-y-4">
        <div className="glass-card rounded-3xl p-1 border-white/10 overflow-hidden relative">
          <div className="absolute top-0 right-0 p-4 z-20">
            <div className="bg-black/50 backdrop-blur-md px-3 py-1 rounded-full border border-white/10 text-xs font-mono text-neon-green flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
              LIVE PREVIEW
            </div>
          </div>

          {/* Editor Mockup with REAL Data */}
          <div className="bg-[#0A0A0B] rounded-[1.4rem] p-6 h-[500px] overflow-auto relative font-mono text-sm">
             <pre className="text-gray-300 whitespace-pre-wrap font-mono text-xs leading-relaxed">
                 {tabContent || "No tablature data found."}
             </pre>
          </div>
        </div>
        
        {/* Share Bar */}
        <div className="flex gap-4">
          <Button variant="outline" className="flex-1 bg-white/5 border-white/10 hover:bg-white/10 h-12 rounded-xl text-white">
            <Share2 className="w-4 h-4 mr-2" /> Share
          </Button>
          <a href={downloadUrl} target="_blank" rel="noopener noreferrer" className="flex-1">
            <Button variant="premium" className="w-full h-12 rounded-xl">
              <Download className="w-4 h-4 mr-2" /> Download Bundle
            </Button>
          </a>
        </div>
      </div>

      {/* Sidebar Call to Action */}
      <div className="md:col-span-4 space-y-6">
         <div className="glass-card rounded-3xl p-8 relative overflow-hidden group">
            <div className="absolute inset-0 bg-neon-purple/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
            
            <h3 className="font-display font-bold text-3xl mb-2 text-white">YourMT3+</h3>
            <p className="text-gray-400 mb-8 border-b border-white/10 pb-4">
              {statusMsg.split("✅")[0] || "Transcription successful."}
            </p>

            <ul className="space-y-4 mb-8">
               {['Polyphonic Transcription', 'MIDI & GP5 Output', 'Stem Separation', 'API Access'].map((feat, i) => (
                 <motion.li 
                   key={feat}
                   initial={{ opacity: 0, x: 20 }}
                   animate={{ opacity: 1, x: 0 }}
                   transition={{ delay: 0.5 + (i * 0.1) }}
                   className="flex items-center gap-3 text-sm"
                 >
                   <div className="w-6 h-6 rounded-full bg-neon-cyan/20 flex items-center justify-center">
                     <CheckCircle className="w-3.5 h-3.5 text-neon-cyan" />
                   </div>
                   {feat}
                 </motion.li>
               ))}
            </ul>

            <Button 
              className="w-full bg-white text-black hover:bg-neon-cyan font-bold h-14 rounded-xl text-lg transition-all duration-300"
              onClick={() => window.open("https://huggingface.co/spaces/scottymills/tab-agent-pro", "_blank")}
            >
              Run on ZeroGPU
            </Button>
         </div>
         
         <Button 
          variant="ghost" 
          className="w-full text-white/50 hover:text-white"
          onClick={onReset}
         >
           Transcribe Another File
         </Button>
      </div>
    </div>
  );
};
