import React, {useEffect, useState} from "react";
import axios from "axios";
import {useNavigate} from "react-router-dom";

const Home = () => {
    const [search, setSearch] = useState("");
    const [results, setResults] = useState([]);
    const navigate = useNavigate();
    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:8000/homepage/");
                setResults(response.data.front_page || []);
            } catch (error) {
                console.error("Error fetching initial data:", error);
            }
        };
        fetchInitialData();
    }, []);
    const handleSearch = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post("http://127.0.0.1:8000/search/", {search});
            setResults(response.data.names || []);
        } catch (error) {
            console.error("Error fetching search results:", error);
            setResults([]);
        }
    };

    const redirectStockDetails = (stockName) => {
        navigate(`/stock/${stockName}`);
    };

    return (
        <>
            <div className="d-flex align-items-center">
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
            <div className="row">
                {results.map((name, index) => (
                    <div className="col-md-3 mb-4" key={index}>
                        <div className="card">
                            <h5 className="card-title text-center">{name}</h5>
                            <img src="/stockimg.png" className="card-img-top" alt={name}/>
                            <div className="card-body">
                                <button className="btn btn-primary"onClick={() => redirectStockDetails(name)}>
                                    View Details
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </>
    )
}
export default Home;