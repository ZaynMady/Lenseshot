import { useState } from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css'

import AuthPage from './pages/auth.jsx'
import Maintemp from './pages/main_temp.jsx'
import Home from './pages/homepage.jsx'
import Dashboard from './pages/dashboard.jsx'
import Projects from './pages/projects.jsx'
import Screenplay  from './pages/screenplay.jsx';
import ProjectcontrolPage from './pages/ProjectcontrolPage.jsx';
import AccountPage from './pages/accountpage.jsx';

function App() {
  return (
  <Router>

  <Routes> 

  <Route path="/Auth" element={<AuthPage />} />
  <Route path="*" element={<AuthPage />} />

  <Route element={<Maintemp />}>
  <Route path="/homepage" element={<Home />} />
  <Route path="/account" element={<AccountPage />} />
  <Route path="/projects" element={<Dashboard />} />
  <Route path="/projects/:id" element={<Projects />}>
    <Route path="edit" element={<ProjectcontrolPage />} />
    <Route path="screenplay" element={<Screenplay />} />
    <Route path="visualization" element={<div>Visualization Page</div>} />
    <Route path="budget" element={<div>Budget Page</div>} />
    <Route path="scheduling" element={<div>Scheduling Page</div>} />
  </Route>
  <Route path="/contacts" element={<div>Contacts Page</div>} />
  <Route path="/account" element={<div>Account Page</div>} />
  
  </Route>

  </Routes>
  </Router>
  );

}

export default App
