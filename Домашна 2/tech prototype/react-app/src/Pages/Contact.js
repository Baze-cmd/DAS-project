import React from 'react';

const Contact = () => {
    return (
        <div className="container d-flex justify-content-center">
            <form className="w-50 p-4 border rounded shadow-sm">
                <div className="mb-3">
                    <label htmlFor="email" className="form-label">E-mail</label>
                    <input type="email" id="email" name="E-mail" className="form-control" />
                </div>
                <div className="mb-3">
                    <label htmlFor="subject" className="form-label">Subject</label>
                    <input type="text" id="subject" name="Subject" className="form-control" />
                </div>
                <div className="mb-3">
                    <label htmlFor="description" className="form-label">Description</label>
                    <textarea id="description" name="Description" className="form-control" rows="5"></textarea>
                </div>
                <button type="submit" className="btn btn-primary w-100">Submit</button>
            </form>
        </div>
    );
}

export default Contact;
