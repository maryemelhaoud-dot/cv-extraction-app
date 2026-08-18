import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

import Navbar from '../../components/layout/Navbar/Navbar';
import { getCandidat } from '../../services/candidatService';

import SecurityOutlinedIcon from '@mui/icons-material/SecurityOutlined';
import LightbulbOutlinedIcon from '@mui/icons-material/LightbulbOutlined';

import './Extraction.css';

const ETAPES = [
    'Lecture du fichier',
    'Extraction du texte (OCR)',
    'Analyse sémantique',
    'Structuration des données',
    'Enregistrement des informations',
];

function Extraction() {
    const navigate = useNavigate();
    const candidatId = useSelector((state) => state.candidate.candidatId);

    const [progress, setProgress] = useState(10);
    const [etapeActuelle, setEtapeActuelle] = useState(0);
    const [erreur, setErreur] = useState(null);

    useEffect(() => {
        if (!candidatId) {
            navigate('/upload');
            return;
        }

        // Timer visuel progressif (monte jusqu'à 90% en attendant le serveur)
        const visualTimer = setInterval(() => {
            setProgress((prev) => {
                if (prev >= 90) return 90;
                const next = prev + 4;
                const nouvelleEtape = Math.min(
                    Math.floor((next / 100) * ETAPES.length),
                    ETAPES.length - 2
                );
                setEtapeActuelle(nouvelleEtape);
                return next;
            });
        }, 800);

        // Polling backend pour vérifier le statut réel
        const pollInterval = setInterval(async () => {
            try {
                const data = await getCandidat(candidatId);
                if (data.statut_traitement === 'traité') {
                    clearInterval(pollInterval);
                    clearInterval(visualTimer);
                    setProgress(100);
                    setEtapeActuelle(ETAPES.length - 1);
                    setTimeout(() => navigate('/result'), 600);
                } else if (data.statut_traitement === 'erreur') {
                    clearInterval(pollInterval);
                    clearInterval(visualTimer);
                    setErreur(data.resume_profil || "L'analyse du CV a échoué. Veuillez vérifier le fichier et réessayez.");
                }
            } catch (err) {
                console.error("Erreur lors de la vérification du statut :", err);
            }
        }, 800);

        return () => {
            clearInterval(visualTimer);
            clearInterval(pollInterval);
        };
    }, [candidatId, navigate]);

    if (erreur) {
        return (
            <div className="extraction-page">
                <Navbar activeStep={1} />
                <main className="extraction-content">
                    <section className="extraction-progress" style={{ textAlign: 'center', padding: '2rem' }}>
                        <h2>Erreur d'analyse</h2>
                        <p style={{ color: '#d32f2f', margin: '1rem 0' }}>{erreur}</p>
                        <button className="primary-button" onClick={() => navigate('/upload')}>
                            Réessayer l'upload
                        </button>
                    </section>
                </main>
            </div>
        );
    }

    return (
        <div className="extraction-page">

            <Navbar activeStep={1} />

            <main className="extraction-content">

                <section className="extraction-progress">

                    <div
                        className="progress-circle"
                        style={{
                            background: `conic-gradient(#00843d 0deg ${progress * 3.6}deg, #e1eee8 ${progress * 3.6}deg 360deg)`
                        }}
                    >
                        <div className="progress-circle-inner">
                            <span>{progress}%</span>
                        </div>
                    </div>

                    <div className="progress-details">

                        <h2>Analyse en cours...</h2>

                        <p className="progress-description">
                            Veuillez patienter pendant que nous traitons votre CV.
                        </p>

                        <div className="progress-bar">
                            <div
                                className="progress-bar-fill"
                                style={{ width: `${progress}%` }}
                            />
                        </div>

                        <div className="extraction-steps">
                            {ETAPES.map((label, index) => {
                                let statutClasse = 'pending';
                                let icone = '○';
                                let statutTexte = 'En attente';

                                if (index < etapeActuelle) {
                                    statutClasse = 'completed';
                                    icone = '✓';
                                    statutTexte = 'Terminé';
                                } else if (index === etapeActuelle) {
                                    statutClasse = 'active';
                                    icone = '⟳';
                                    statutTexte = 'En cours';
                                }

                                return (
                                    <div key={label} className={`extraction-step ${statutClasse}`}>
                                        <span className="step-icon">{icone}</span>
                                        <span className="step-label">{label}</span>
                                        <span className="step-status">{statutTexte}</span>
                                    </div>
                                );
                            })}
                        </div>

                    </div>

                </section>

                <section className="extraction-security">
                    <div className="security-icon">
                        <SecurityOutlinedIcon />
                    </div>
                    <div className="security-content">
                        <h3>Vos données sont sécurisées</h3>
                        <p>Vos fichiers et informations sont traités de manière confidentielle.</p>
                    </div>
                </section>

                <section className="extraction-tip">
                    <div className="tip-icon">
                        <LightbulbOutlinedIcon />
                    </div>
                    <p>
                        Conseil : L'extraction peut prendre quelques secondes
                        selon la taille et la complexité du CV.
                    </p>
                </section>

            </main>

        </div>
    );
}

export default Extraction;