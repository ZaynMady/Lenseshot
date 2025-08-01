import { useState } from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css'
import Login from './pages/login'
import Register from './pages/register'
import Maintemp from './pages/main_temp'
import Home from './pages/homepage'
import Dashboard from './pages/dashboard'

function App() {
  return (
  <Router>

  <Routes> 

  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />

  <Route element={<Maintemp />}>
  <Route path="/" element={<Home />} />
  <Route path="/projects" element={<Dashboard />} />
  <Route path="/contacts" element={<div>Contacts Page</div>} />
  <Route path="/account" element={<div>Account Page</div>} />
  
  </Route>

  </Routes>
  </Router>
  );

}

export default App
