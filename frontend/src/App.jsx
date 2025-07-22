import { useState } from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css'
import Login from './pages/login.jsx'
import Register from './pages/register.jsx'
import Maintemp from './pages/main_temp.jsx'
import Home from './pages/homepage.jsx'
import Projects from './pages/projects.jsx'

function App() {
  return (
  <Router>

  <Routes> 

  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />

  <Route element={<Maintemp />}>
  <Route path="/" element={<Home />} />
  <Route path="/projects" element={<Projects />} />
  <Route path="/contacts" element={<div>Contacts Page</div>} />
  <Route path="/account" element={<div>Account Page</div>} />
  </Route>
  


  </Routes>
  </Router>
  );

}

export default App
