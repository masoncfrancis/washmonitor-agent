import {useState} from 'react';

const LaundryDashboard = () => {
    const [washerActive, setWasherActive] = useState(false);
    const [dryerActive, setDryerActive] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleButtonClick = (type: 'washer' | 'dryer') => {
        setLoading(true);
        setTimeout(() => {
            if (type === 'washer') {
                setWasherActive(!washerActive);
                if (dryerActive) setDryerActive(false);
            } else {
                setDryerActive(!dryerActive);
                if (washerActive) setWasherActive(false);
            }
            setLoading(false);
        }, 300);
    };

    return (
        <div className="flex h-screen w-screen">
            {(!dryerActive && !washerActive) && (
                <>
                    <div
                        className={`flex-1 flex flex-col justify-center items-center text-4xl cursor-pointer text-center break-words bg-green-500 text-white`}
                        onClick={() => handleButtonClick('washer')}
                    >
                        {washerActive ? 'Monitoring Washer' : 'Washer'}
                        {washerActive && <div className="loader mt-4"></div>}
                    </div>
                    <div
                        className={`flex-1 flex flex-col justify-center items-center text-4xl cursor-pointer text-center break-words bg-blue-500 text-white`}
                        onClick={() => handleButtonClick('dryer')}
                    >
                        {dryerActive ? 'Monitoring Dryer' : 'Dryer'}
                        {dryerActive && <div className="loader mt-4"></div>}
                    </div>
                </>
            )}
            {washerActive && !dryerActive && (
                <div
                    className="flex-1 flex flex-col justify-center items-center text-4xl cursor-pointer text-center break-words bg-green-500 text-white h-full w-full"
                    onClick={() => handleButtonClick('washer')}
                >
                    Monitoring Washer
                    <div className="loader mt-4"></div>
                </div>
            )}
            {dryerActive && !washerActive && (
                <div
                    className="flex-1 flex flex-col justify-center items-center text-4xl cursor-pointer text-center break-words bg-blue-500 text-white h-full w-full"
                    onClick={() => handleButtonClick('dryer')}
                >
                    Monitoring Dryer
                    <div className="loader mt-4"></div>
                </div>
            )}
            {loading && (
                <div
                    className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 flex justify-center items-center z-50 transition-opacity duration-500">
                    <div
                        className="loader w-16 h-16 border-4 border-t-black border-b-black border-solid rounded-full animate-spin"></div>
                </div>
            )}
        </div>
    );
};

export default LaundryDashboard;