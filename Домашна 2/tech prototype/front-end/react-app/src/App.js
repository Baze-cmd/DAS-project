import React, {useState} from "react";
import axios from "axios";

const App = () => {
    const [search, setSearch] = useState("");
    const [results, setResults] = useState([]);

    const handleSearch = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post("http://127.0.0.1:8000/search/", {search});
            setResults(response.data.names || []);
        } catch (error) {
            console.error("Error fetching data:", error);
            setResults([]);
        }
    };

    return (
        <div className="container">
            <header className="my-4">
                <h1 className="display-4">MK Stocks Analyzr</h1>
                <div className="d-flex align-items-center justify-content-between">
                    <div className="d-flex align-items-center">
                        <img src="/logo.png" alt="Logo" width="100" height="100"/>
                        <a href="/" className="btn btn-primary m-2">Home</a>
                        <div className="d-flex justify-content-center align-items-center">
                            <form onSubmit={handleSearch} className="d-flex">
                                <input
                                    type="text"
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                    placeholder="Search..."
                                    required
                                    className="form-control mr-2"
                                />
                                <button type="submit" className="btn btn-primary">🔎</button>
                            </form>
                        </div>
                    </div>
                    <div>
                        <a href="/about" className="btn btn-secondary m-2">About</a>
                        <a href="/contact" className="btn btn-success m-2">Contact</a>
                    </div>
                </div>
            </header>

            <ul>
                {results.map((name, index) => (
                    <li key={index}>{name}</li>
                ))}
            </ul>
        </div>
    );
};

export default App;
