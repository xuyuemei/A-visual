import { useState } from 'react'
import './App.css'
import { Routes, Route } from 'react-router-dom';  // ✅ 删除 BrowserRouter

import Main from './pages/Main/Main'
import HomePage from './pages/Home/HomePage'
import Navbar from './components/Navbar/Navbar'
// import UserManagement from './pages/Admin/UserManagement';
// import TemplatesManagement from './pages/Admin/TemplatesManagement';
// import Setting from './pages/User/Setting/Setting';
// import History from './pages/History/History';
// import Login from './pages/User/Login/Login';

function App() {
  const [count, setCount] = useState(0)


  return (
    <>
      {/* 全局导航栏 */}
      <Navbar />
      
      {/* ✅ Router 外层由 index.tsx 包好了 */}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/main" element={<Main />} />
        {/*
         <Route path="/usermanagement" element={<UserManagement />} />
         <Route path="/templatesmanagement" element={<TemplatesManagement />} />
         <Route path="/setting" element={<Setting />} />
         <Route path="/history" element={<History />} />
         <Route path="/login" element={<Login />} /> 
         */}
      </Routes>
    </>
  )
}

export default App;