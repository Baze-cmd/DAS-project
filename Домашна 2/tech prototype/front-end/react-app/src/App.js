import React from "react";
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./Pages/Home";
import About from "./Pages/About";
import Contact from "./Pages/Contact";
import StockDetails from "./components/StockDetails";

const App = () => {

    return (
        <Router>
            <Navbar/>
            <Routes>
                <Route exact path="/" element={<Home/>}></Route>
                <Route path="/about" element={<About/>}></Route>
                <Route path="/contact" element={<Contact/>}></Route>
                <Route path="/stock/:name" element={<StockDetails />} />

            </Routes>
        </Router>
    );
};

export default App;
