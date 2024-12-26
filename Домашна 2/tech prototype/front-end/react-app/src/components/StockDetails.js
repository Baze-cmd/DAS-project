import React, {useEffect, useState} from 'react';
import {useParams} from 'react-router-dom';
import axios from 'axios';
import {Line} from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    LineElement,
    PointElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend);

const StockDetails = () => {
    const {name} = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [timePeriod, setTimePeriod] = useState('5 years');
    const [graphData, setGraphData] = useState([]);
    const [indicators, setIndicators] = useState([]);
    const timePeriods = ['All time', '5 years', '1 year', '1 month', '1 week', '1 day'];

    useEffect(() => {
        const fetchStockDetails = async () => {
            try {
                const backendUrl = `http://localhost:8000/stock_data/${name}/`;
                const response = await axios.get(backendUrl);

                setData(response.data.data);
            } catch (error) {
                console.error("Error fetching stock details:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchStockDetails();
    }, [name]);

    useEffect(() => {
        if (!data) return;

        const now = new Date();
        let cutoffDate;

        switch (timePeriod) {
            case '5 years':
                cutoffDate = new Date(now.getFullYear() - 5, now.getMonth(), now.getDate());
                break;
            case '1 year':
                cutoffDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
                break;
            case '1 month':
                cutoffDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
                break;
            case '1 week':
                cutoffDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7);
                break;
            case '1 day':
                cutoffDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
                break;
            default:
                cutoffDate = null;
        }

        const dataToGraph = cutoffDate
            ? data.filter(item => new Date(item.Date.split('.').reverse().join('-')) >= cutoffDate)
            : data;

        setGraphData(dataToGraph);
    }, [timePeriod, data]);

    useEffect(() => {
        const fetchIndicators = async () => {
            try {
                console.log(timePeriod);
                const backendUrl = `http://localhost:8000/stock_data/${name}/`;
                const response = await axios.post(backendUrl, {
                    timePeriod: timePeriod
                }, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                console.log(response.data.indicators);
                setIndicators(response.data.indicators);
            } catch (error) {
                console.error("Error fetching indicators:", error);
            }
        }
        fetchIndicators();
    }, [timePeriod]);

    const handleClick = (label) => {
        setTimePeriod(label);
    };

    if (loading) return <p>Loading...</p>;

    if (!data) return <p>Error: No data available.</p>;

    const chartData = {
        labels: graphData.map(item => item.Date),
        datasets: [
            {
                label: 'Price',
                data: graphData.map(row => row.Last_trade_price),
                borderColor: 'rgba(75,192,192,1)',
                backgroundColor: 'rgba(75,192,192,0.2)',
                tension: 0.4,
                pointRadius: 3,
                fill: true,
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: `Price Changes Over ${timePeriod}`,
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Date',
                },
            },
            y: {
                title: {
                    display: true,
                    text: 'Price',
                },
            },
        },
    };

    const getAction = (indicator, value) => {
        if (value == null) return 'Hold'
        switch (indicator) {
            case 'Relative Strength Index':
                if (value > 70) return 'Sell';
                if (value < 30) return 'Buy';
                return 'Hold';
            case 'Stochastic RSI %D':
                if (value > 80) return 'Sell';
                if (value < 20) return 'Buy';
                return 'Hold';
            case 'Commodity Channel Index':
                if (value > 100) return 'Sell';
                if (value < -100) return 'Buy';
                return 'Hold';
            case 'Trix':
                if (value > 0) return 'Buy';
                if (value < 0) return 'Sell';
                return 'Hold';
            case 'Awesome Oscillator':
                if (value > 0) return 'Buy';
                if (value < 0) return 'Sell';
                return 'Hold';
            case 'Simple Moving Average':
            case 'Exponential Moving Average':
            case 'Kaufman’s Adaptive Moving Average':
            case 'Weighted Moving Average':
            case 'Ichimoku':
                return 'Hold';
            default:
                return 'Hold';
        }
    };

    return (
        <div>
            <h1 style={{maxWidth: "fit-content", marginLeft: "auto", marginRight: "auto"}}>{name}</h1>
            <div>
                <h4>Select time period</h4>
                <div>
                    {timePeriods.map((label, index) => (
                        <button
                            id={label}
                            className={`btn ${timePeriod === label ? 'btn-secondary' : 'btn-light'}`}
                            style={{marginRight: '10px', marginLeft: '10px'}}
                            key={index}
                            onClick={() => handleClick(label)}
                        >
                            {label}
                        </button>
                    ))}
                </div>
            </div>
            <div style={{marginTop: '20px', display: 'flex', justifyContent: 'space-between'}}>
                <div style={{flex: 1}}>
                    <Line data={chartData} options={chartOptions}/>
                </div>

                <div style={{flex: 1, marginLeft: '20px'}}>
                    <div style={{marginBottom: '20px'}}>
                        <h4>Oscillators</h4>
                        <table style={{width: '100%', textAlign: 'center', borderCollapse: 'collapse'}}>
                            <thead>
                            <tr>
                                <th style={{width: '40%', padding: '5px'}}>Name</th>
                                <th style={{width: '40%', padding: '5px'}}>Value</th>
                                <th style={{width: '40%', padding: '5px'}}>Action</th>
                            </tr>
                            </thead>
                            <tbody>
                            {(indicators.Oscillators && Object.entries(indicators.Oscillators).length > 0) ? (
                                Object.entries(indicators.Oscillators).map(([key, value]) => (
                                    <tr key={key}>
                                        <td style={{padding: '5px'}}>{key}</td>
                                        <td style={{padding: '5px'}}>{value == null ? 'NA' : value}</td>
                                        <td
                                            style={{
                                                padding: '5px',
                                                color: getAction(key, value) === 'Buy' ? 'blue' : getAction(key, value) === 'Sell' ? 'red' : 'gray'
                                            }}
                                        >
                                            {getAction(key, value)}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3">No Oscillators available</td>
                                </tr>
                            )}
                            </tbody>
                        </table>
                    </div>

                    <div>
                        <h4>Moving Averages</h4>
                        <table style={{width: '100%', textAlign: 'center', borderCollapse: 'collapse'}}>
                            <thead>
                            <tr>
                                <th style={{width: '40%', padding: '5px'}}>Name</th>
                                <th style={{width: '40%', padding: '5px'}}>Value</th>
                                <th style={{width: '40%', padding: '5px'}}>Action</th>
                            </tr>
                            </thead>
                            <tbody>
                            {(indicators["Moving averages"] && Object.entries(indicators["Moving averages"]).length > 0) ? (
                                Object.entries(indicators["Moving averages"]).map(([key, value]) => (
                                    <tr key={key}>
                                        <td style={{padding: '5px'}}>{key}</td>
                                        <td style={{padding: '5px'}}>{value == null ? 'NA' : value}</td>
                                        <td
                                            style={{
                                                padding: '5px',
                                                color: getAction(key, value) === 'Buy' ? 'blue' : getAction(key, value) === 'Sell' ? 'red' : 'gray'
                                            }}
                                        >
                                            {getAction(key, value)}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3">No Moving Averages available</td>
                                </tr>
                            )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );

};

export default StockDetails;
