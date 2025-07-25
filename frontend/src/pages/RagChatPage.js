import React, { useState, useEffect, useRef } from 'react';

const RagChatPage = () => {
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Hello! Tell me how you feel today and I’ll suggest some songs from my playlist 🎶' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const newMessages = [...messages, { type: 'user', text: input }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat-conversational-rag", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          session_id: "george",
        }),
      });

      const data = await res.json();
      const reply = data.reply || "🤖 Sorry, something went wrong.";
      setMessages([...newMessages, { type: 'bot', text: reply }]);
    } catch (err) {
      setMessages([...newMessages, { type: 'bot', text: 'Error reaching server ❌' }]);
    }

    setInput('');
    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="flex flex-col h-screen bg-neutral-950 text-white font-poppins text-lg">
      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-3xl mx-auto p-4 rounded-2xl whitespace-pre-wrap ${
              msg.type === 'user'
                ? 'bg-green-600 text-white ml-auto'
                : 'bg-neutral-800 text-gray-100 mr-auto'
            }`}
          >
            {msg.text}
          </div>
        ))}
        {loading && (
          <div className="max-w-3xl mx-auto p-4 rounded-2xl bg-neutral-800 text-gray-300 animate-pulse">
            🤖 Typing...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="bg-neutral-900 px-4 py-4 border-t border-neutral-800">
        <div className="flex max-w-3xl mx-auto gap-2">
          <input
            type="text"
            className="flex-1 p-3 rounded-xl bg-neutral-800 text-white text-lg focus:outline-none"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={loading}
          />
          <button
            onClick={handleSend}
            className={`px-5 py-3 rounded-xl font-semibold ${
              loading
                ? 'bg-gray-600 cursor-not-allowed'
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
            disabled={loading}
          >
            {loading ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RagChatPage;
