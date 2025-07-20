import React, { useState } from 'react';

const ChatPage = () => {
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Hello! Tell me how you feel today and I’ll suggest some songs 🎶' },
  ]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;

    // Append user message
    const newMessages = [...messages, { type: 'user', text: input }];
    setMessages(newMessages);

    try {
      const res = 
      await fetch("http://localhost:8000/chat", {
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
      const reply = data.reply || data || "🤖 Sorry, something went wrong.";
      setMessages([...newMessages, { type: 'bot', text: reply }]);
    } catch (err) {
      setMessages([...newMessages, { type: 'bot', text: 'Error reaching server ❌' }]);
    }

    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="max-w-3xl mx-auto mt-8 bg-neutral-800 rounded-xl p-6 shadow-md">
      <div className="h-96 overflow-y-auto space-y-4 mb-4 p-4 bg-neutral-900 rounded-md">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`text-sm p-3 rounded-lg max-w-xs ${
              msg.type === 'user'
                ? 'bg-green-600 ml-auto text-white'
                : 'bg-neutral-700 text-gray-100'
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div className="flex items-center space-x-2">
        <input
          type="text"
          className="flex-1 p-2 rounded-lg bg-neutral-700 text-white focus:outline-none"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
        />
        <button
          onClick={handleSend}
          className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
