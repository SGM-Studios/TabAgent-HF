import { motion } from "framer-motion";

export const HeroBackground = () => {
  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden -z-10 bg-background">
      {/* Mesh Gradients */}
      <div className="absolute top-0 left-0 w-full h-full opacity-30">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute -top-[10%] -left-[10%] w-[50%] h-[50%] rounded-full bg-neon-purple/30 blur-[100px]"
        />
        <motion.div
          animate={{
            scale: [1, 1.1, 1],
            x: [0, 50, 0],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-[20%] right-[0%] w-[40%] h-[40%] rounded-full bg-neon-cyan/20 blur-[120px]"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute bottom-[-10%] left-[20%] w-[60%] h-[60%] rounded-full bg-primary/20 blur-[150px]"
        />
      </div>

      {/* Grid Pattern Overlay */}
      <div 
        className="absolute inset-0 opacity-[0.2]"
        style={{
          backgroundImage: `linear-gradient(to right, #333 1px, transparent 1px),
          linear-gradient(to bottom, #333 1px, transparent 1px)`,
          backgroundSize: '4rem 4rem',
          maskImage: 'radial-gradient(ellipse 60% 50% at 50% 0%, #000 70%, transparent 100%)'
        }}
      />
      
      {/* Noise Texture (Globally handled by index.css .noise-bg, but can add specific overlay here if needed) */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/50 to-background" />
    </div>
  );
};
