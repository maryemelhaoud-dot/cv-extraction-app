import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import './SplashScreen.css';

import ocpLogo from '../../assets/logos/ocp-logo.png';
import factoryBg from '../../assets/images/ocp-jorf-lasfar.png';

function SplashScreen() {

    const [progress, setProgress] = useState(0);

    const navigate = useNavigate();
    useEffect(() => {
    let frameId;
    let start = null;
    let navigationTimer;

    const duration = 2500;

    const tick = (timestamp) => {

        if (start === null) {
            start = timestamp;
        }

        const elapsed = timestamp - start;

        const pct = Math.min(
            100,
            (elapsed / duration) * 100
        );

        setProgress(pct);

        if (pct < 100) {

            frameId = requestAnimationFrame(tick);

        } else {

            // La progression est réellement terminée
            setProgress(100);

            // On laisse le navigateur afficher les 100 %
            navigationTimer = setTimeout(() => {
                navigate('/upload');
            }, 300);
        }
    };

    frameId = requestAnimationFrame(tick);

    return () => {
        cancelAnimationFrame(frameId);
        clearTimeout(navigationTimer);
    };

}, [navigate]);

    return (

        <div className="loading-page">

            <div className="loading-card">

                <div className="loading-logo">

                    <img
                        src={ocpLogo}
                        alt="Logo OCP"
                    />

                </div>


                <p className="loading-subtitle">
                    Automatically extract key information from your resumes in seconds
                </p>


                <div
                    className="loading-visual"
                    style={{
                        backgroundImage: `url(${factoryBg})`
                    }}
                >

                    <div className="loading-visual-fade" />

                </div>


                <div className="loading-progress-wrapper">

                    <div className="loading-progress-track">

                        <div
                            className="loading-progress-fill"
                            style={{
                                width: `${progress}%`
                            }}
                        />

                    </div>


                    <p className="loading-progress-label">
                        Chargement en cours...
                    </p>

                </div>

            </div>

        </div>

    );
}

export default SplashScreen;