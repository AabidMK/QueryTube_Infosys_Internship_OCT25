import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Search from "./pages/Search";
import Summarize from "./pages/Summarize";
import ChannelVideos from './pages/ChannelVideos';
import "./styles/index.css";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <div className="container mx-auto p-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/summarize/:videoId" element={<Summarize />} />
          <Route path="/channel/:channelName" element={<ChannelVideos />} />


        </Routes>
      </div>
    </BrowserRouter>
  );
}
