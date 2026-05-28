"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Mic, Volume2, AlertTriangle } from "lucide-react";
import { useOrbStore } from "@/store/orbStore";

const orbConfig = {
  idle: {
    gradient: "conic-gradient(from 0deg, #8b5cf6, #d946ef, #3b82f6, #06b6d4, #8b5cf6)",
    innerGlow: "rgba(139, 92, 246, 0.15)",
    outerGlow: "rgba(139, 92, 246, 0.2)",
    icon: Sparkles,
    iconColor: "#c4b5fd",
    pulseSpeed: 3,
    rotateSpeed: 8,
    scale: [1, 1.04, 1],
  },
  listening: {
    gradient: "conic-gradient(from 0deg, #3b82f6, #06b6d4, #3b82f6)",
    innerGlow: "rgba(59, 130, 246, 0.2)",
    outerGlow: "rgba(59, 130, 246, 0.3)",
    icon: Mic,
    iconColor: "#93c5fd",
    pulseSpeed: 1,
    rotateSpeed: 2,
    scale: [1, 1.12, 1],
  },
  thinking: {
    gradient: "conic-gradient(from 0deg, #8b5cf6, #a855f7, #d946ef, #8b5cf6)",
    innerGlow: "rgba(168, 85, 247, 0.2)",
    outerGlow: "rgba(168, 85, 247, 0.3)",
    icon: Sparkles,
    iconColor: "#d8b4fe",
    pulseSpeed: 0.8,
    rotateSpeed: 1.5,
    scale: [0.96, 1.08, 0.96],
  },
  speaking: {
    gradient: "conic-gradient(from 0deg, #22c55e, #06b6d4, #22c55e)",
    innerGlow: "rgba(34, 197, 94, 0.2)",
    outerGlow: "rgba(34, 197, 94, 0.25)",
    icon: Volume2,
    iconColor: "#86efac",
    pulseSpeed: 0.5,
    rotateSpeed: 3,
    scale: [1, 1.06, 1],
  },
  error: {
    gradient: "conic-gradient(from 0deg, #ef4444, #f97316, #ef4444)",
    innerGlow: "rgba(239, 68, 68, 0.2)",
    outerGlow: "rgba(239, 68, 68, 0.25)",
    icon: AlertTriangle,
    iconColor: "#fca5a5",
    pulseSpeed: 0.3,
    rotateSpeed: 0,
    scale: [1, 1, 1],
  },
};

export default function AIOrb() {
  const orbState = useOrbStore((s) => s.state);
  const setOrbState = useOrbStore((s) => s.setState);
  const config = orbConfig[orbState];
  const Icon = config.icon;

  const handleClick = () => {
    if (orbState === "idle") {
      setOrbState("listening");
    } else if (orbState === "listening") {
      setOrbState("idle");
    } else if (orbState === "error") {
      setOrbState("idle");
    }
  };

  return (
    <motion.div
      style={{
        position: "relative",
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
      onClick={handleClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Outer glow */}
      <motion.div
        animate={{
          scale: config.scale,
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: config.pulseSpeed,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        style={{
          position: "absolute",
          inset: -28,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${config.outerGlow} 0%, transparent 70%)`,
          filter: "blur(16px)",
        }}
      />

      {/* Ring pulse (listening/thinking only) */}
      <AnimatePresence>
        {(orbState === "listening" || orbState === "thinking") && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0.6 }}
            animate={{ scale: 1.6, opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{
              duration: config.pulseSpeed * 1.5,
              repeat: Infinity,
              ease: "easeOut",
            }}
            style={{
              position: "absolute",
              width: 130,
              height: 130,
              borderRadius: "50%",
              border: `2px solid ${config.iconColor}`,
            }}
          />
        )}
      </AnimatePresence>

      {/* Rotating gradient ring */}
      <motion.div
        animate={{
          rotate: config.rotateSpeed > 0 ? 360 : 0,
        }}
        transition={{
          duration: config.rotateSpeed,
          repeat: Infinity,
          ease: "linear",
        }}
        style={{
          width: 120,
          height: 120,
          borderRadius: "50%",
          background: config.gradient,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: `0 0 40px ${config.innerGlow}, 0 0 80px ${config.outerGlow}`,
        }}
      >
        {/* Inner dark circle */}
        <motion.div
          animate={{ scale: config.scale }}
          transition={{
            duration: config.pulseSpeed,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          style={{
            width: 106,
            height: 106,
            borderRadius: "50%",
            background: "var(--bg-primary)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={orbState}
              initial={{ scale: 0, rotate: -90 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0, rotate: 90 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
            >
              <Icon size={34} color={config.iconColor} />
            </motion.div>
          </AnimatePresence>
        </motion.div>
      </motion.div>

      {/* State label */}
      <motion.span
        key={orbState}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          position: "absolute",
          bottom: -28,
          fontSize: 11,
          fontWeight: 600,
          color: config.iconColor,
          textTransform: "uppercase",
          letterSpacing: "0.1em",
        }}
      >
        {orbState}
      </motion.span>

      {/* Waveform bars (speaking state) */}
      <AnimatePresence>
        {orbState === "speaking" && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: "absolute",
              bottom: -12,
              display: "flex",
              gap: 3,
              alignItems: "center",
            }}
          >
            {[0, 1, 2, 3, 4].map((i) => (
              <motion.div
                key={i}
                animate={{ scaleY: [0.4, 1.4, 0.4] }}
                transition={{
                  duration: 0.6,
                  repeat: Infinity,
                  delay: i * 0.1,
                  ease: "easeInOut",
                }}
                style={{
                  width: 3,
                  height: 14,
                  borderRadius: 2,
                  background: config.iconColor,
                  transformOrigin: "bottom",
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
