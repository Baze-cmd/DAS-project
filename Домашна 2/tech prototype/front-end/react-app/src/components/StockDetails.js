import React, {useEffect, useState} from 'react';
import {useParams} from 'react-router-dom';
import axios from 'axios';

const StockDetails = () => {
    const {name} = useParams();
    const [stockData, setStockData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStockDetails = async () => {
            try {
                const backendUrl = `http://localhost:8000/stock_detail/${name}/`;
                const response = await axios.get(backendUrl);

                setStockData(response.data);
            } catch (error) {
                console.error("Error fetching stock details:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStockDetails();
    }, [name]);

    // Render logic
    if (loading) return <p>Loading...</p>;

    if (!stockData) return <p>Error: No data available.</p>;

    return (
        <div>
            <h1>Stock Details for {stockData.name}</h1>
        </div>
    );
}

export default StockDetails;
