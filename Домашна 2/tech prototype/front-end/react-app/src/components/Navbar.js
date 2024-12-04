import React from "react";
import {Link} from "react-router-dom";

const Navbar = () => {
    return (
        <header className="my-4">
            <h1 className="display-4">MK Stocks Analyzr</h1>
            <div className="d-flex align-items-center justify-content-between">
                <div className="d-flex align-items-center">
                    <img src="/logo.png" alt="Logo" width="100" height="100"/>
                    <Link exact to="/" className="btn btn-primary m-2">Home</Link>
                </div>
                <div>
                    <Link to="/about" className="btn btn-success m-2">About</Link>
                    <Link to="/contact" className="btn btn-success m-2">Contact</Link>
                    <Link to="/login" className="btn btn-success m-2">Login</Link>
                </div>
            </div>
        </header>
    );
};

export default Navbar;