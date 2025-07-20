import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import ChatPage from './pages/ChatPage';

function App() {
  return (
    <Router>
      <div className="bg-zinc-900 min-h-screen text-white">
        <Navbar />
        <div className="p-6">
          <Routes>
            <Route path="/" element={<div>User Guide</div>} />
            <Route path="/chatbot" element={<ChatPage />} />
            <Route path="/about" element={<div>About this app</div>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
