import React from "react";

const LoginPage = () => {
    return (
        <div className="container d-flex justify-content-center">
            <form className="w-50 p-4 border rounded shadow-sm">
                <div className="mb-3">
                    <label htmlFor="email" className="form-label">Username:</label>
                    <input type="email" id="email" name="E-mail" className="form-control"/>
                </div>
                <div className="mb-3">
                    <label htmlFor="subject" className="form-label">Password:</label>
                    <input type="text" id="subject" name="Subject" className="form-control"/>
                </div>
                <button type="submit" className="btn btn-primary w-100">Login</button>
            </form>
        </div>
    );
};
export default LoginPage;