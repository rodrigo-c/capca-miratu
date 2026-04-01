import { HashRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import Detail from './pages/Detail';
import Identification from './pages/Identification';
import Questions from './pages/Questions';
import Submit from './pages/Submit';
import './App.css';

export default function App() {
  return (
    <HashRouter>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/consulta/:urlCode" element={<Detail />} />
        <Route path="/consulta/:urlCode/identificacion" element={<Identification />} />
        <Route path="/consulta/:urlCode/preguntas" element={<Questions />} />
        <Route path="/consulta/:urlCode/enviar" element={<Submit />} />
      </Routes>
    </HashRouter>
  );
}
