import React from 'react';

const GuidePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-950 to-black text-white font-poppins px-6 py-10 animate-fadeIn">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-4xl sm:text-5xl font-bold mb-6 text-green-400">
          🎧 How to Use the Music ChatBot
        </h2>

        <p className="mb-4 text-lg">Ready to vibe? Follow these steps:</p>

        <ul className="list-disc pl-6 space-y-4 text-lg">
          <li>💬 <strong>Chat your mood</strong>: Tell the bot how you're feeling.</li>
          <li>🎶 <strong>Get songs</strong>: It'll send back 10 tailored tracks.</li>
          <li>⬇️ <strong>Download</strong>: Say “yes” and get WAV files locally.</li>
          <li>🔁 <strong>Refine</strong>: Ask for changes if you're not 100% vibing.</li>
        </ul>

        <p className="mt-6">⚡ Try different moods — the more you chat, the smarter it gets!</p>
      </div>
    </div>
  );
};

export default GuidePage;
