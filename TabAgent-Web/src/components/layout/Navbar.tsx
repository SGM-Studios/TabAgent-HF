import { Music } from 'lucide-react';
import { Button } from '../ui/button';
import { MagneticWrapper } from '../ui/MagneticWrapper';

export const Navbar = () => {
  return (
    <nav className="fixed w-full z-50 top-0 border-b border-white/10 bg-[#0A0A0A]/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative group">
            <div className="absolute inset-0 bg-neon-purple blur-md opacity-50 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="h-10 w-10 bg-black border border-white/20 rounded-xl relative flex items-center justify-center">
              <Music className="w-5 h-5 text-white" />
            </div>
          </div>
          <span className="font-display font-bold text-xl tracking-tight text-white drop-shadow-[0_2px_10px_rgba(0,0,0,0.5)]">
            Tab Agent <span className="text-neon-cyan text-xs align-super font-mono ml-0.5" style={{ textShadow: '0 0 10px rgba(0,240,255,0.5)' }}>PRO</span>
          </span>
        </div>
        
        <div className="hidden md:flex gap-6">
          {["Features", "Pricing", "API"].map((item) => (
            <a key={item} href="#" className="text-sm font-medium text-gray-400 hover:text-white transition-colors relative group">
              {item}
              <span className="absolute -bottom-1 left-0 w-0 h-px bg-neon-purple transition-all duration-300 group-hover:w-full" />
            </a>
          ))}
        </div>

        <MagneticWrapper>
          <Button variant="ghost" className="text-sm font-medium text-white border border-white/10 hover:bg-white/10 rounded-full px-6 transition-all duration-300">
            Sign In
          </Button>
        </MagneticWrapper>
      </div>
    </nav>
  );
};
