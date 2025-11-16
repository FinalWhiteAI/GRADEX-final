import React from 'react'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Form from "./Form";


const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/form/:item" element={<Form/>}/> 
      </Routes>
    </Router>
  )
}

export default App