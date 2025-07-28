import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import RagChatPage from './pages/RagChatPage';
import GuidePage from './pages/GuidePage';
import AboutPage from './pages/AboutPage';

function App() {
  return (
    <Router>
      <div className="bg-zinc-900 min-h-screen text-white">
        <Navbar />
        <div className="p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/ragchatbot" />} />
            <Route path="/ragchatbot" element={<RagChatPage />} />
            <Route path="/guide" element={<GuidePage />} />
            <Route path="/about" element={<AboutPage/>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
