import React from 'react';

const AboutPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-neutral-900 to-neutral-950 text-white font-poppins px-6 py-10 animate-fadeIn">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-4xl sm:text-5xl font-bold mb-6 text-green-400">
          👋 About Music ChatBot
        </h2>

        <p className="mb-4 text-lg">
          Music ChatBot is your personal AI-powered DJ 🎛️. Just share your mood — it listens, chats,
          recommends, and downloads music directly for you.
        </p>

        <p className="mb-4 text-lg">
          🛠️ <strong>Tech Stack:</strong>
          <ul className="list-disc pl-6 mt-2 space-y-2">
            <li>⚡ FastAPI + LangChain + Ollama (Gemma)</li>
            <li>🎨 React + Tailwind CSS</li>
            <li>📥 yt_dlp for YouTube downloads</li>
          </ul>
        </p>

        <p className="mt-6 text-lg">🎸 Built with ❤️ by Georgios Birmpakos</p>
      </div>
    </div>
  );
};

export default AboutPage;
