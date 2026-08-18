import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';

import Navbar from '../../components/layout/Navbar/Navbar';
import { getCandidat } from '../../services/candidatService';
import { resetCandidat } from '../../redux/candidateSlice';

import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import SchoolOutlinedIcon from '@mui/icons-material/SchoolOutlined';
import WorkOutlineOutlinedIcon from '@mui/icons-material/WorkOutlineOutlined';
import CodeOutlinedIcon from '@mui/icons-material/CodeOutlined';
import LanguageOutlinedIcon from '@mui/icons-material/LanguageOutlined';
import WorkspacePremiumOutlinedIcon from '@mui/icons-material/WorkspacePremiumOutlined';
import FolderOutlinedIcon from '@mui/icons-material/FolderOutlined';
import InterestsOutlinedIcon from '@mui/icons-material/InterestsOutlined';

import './Result.css';


// Petit composant réutilisable : une étiquette + une valeur, en lecture seule
function Champ({ label, value }) {
    return (
        <div className="form-group">
            <label>{label}</label>
            <p className="valeur-lecture-seule">
                {value || '—'}
            </p>
        </div>
    );
}


function Result() {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const candidatId = useSelector((state) => state.candidate.candidatId);

    const [candidat, setCandidat] = useState(null);
    const [chargement, setChargement] = useState(true);
    const [erreur, setErreur] = useState(null);

    const handleNouveauCV = () => {
        dispatch(resetCandidat());
        navigate('/upload');
    };

    useEffect(() => {
        if (!candidatId) {
            setChargement(false);
            return;
        }

        getCandidat(candidatId)
            .then((data) => setCandidat(data))
            .catch(() => setErreur("Impossible de charger les données du candidat."))
            .finally(() => setChargement(false));
    }, [candidatId]);


    const [activeSection, setActiveSection] = useState(0);


    const sections = [
        {
            label: 'Candidat',
            icon: <PersonOutlineOutlinedIcon />
        },
        {
            label: 'Formations',
            icon: <SchoolOutlinedIcon />
        },
        {
            label: 'Expériences',
            icon: <WorkOutlineOutlinedIcon />
        },
        {
            label: 'Compétences',
            icon: <CodeOutlinedIcon />
        },
        {
            label: 'Langues',
            icon: <LanguageOutlinedIcon />
        },
        {
            label: 'Certifications',
            icon: <WorkspacePremiumOutlinedIcon />
        },
        {
            label: 'Projets',
            icon: <FolderOutlinedIcon />
        },
        {
            label: "Centres d'intérêt",
            icon: <InterestsOutlinedIcon />
        }
    ];


    const goToSection = (index) => {

        if (index < 0 || index >= sections.length) {
            return;
        }

        setActiveSection(index);
    };


    if (chargement) {
        return (
            <div className="result-page">
                <Navbar activeStep={2} />
                <main className="result-content">
                    <p>Chargement des données du candidat...</p>
                </main>
            </div>
        );
    }

    if (erreur) {
        return (
            <div className="result-page">
                <Navbar activeStep={2} />
                <main className="result-content">
                    <p>{erreur}</p>
                </main>
            </div>
        );
    }

    const formations = candidat?.formations || [];
    const experiences = candidat?.experiences || [];
    const competencesTechniques = (candidat?.competences || []).filter(
        (c) => c.categorie === 'Technique'
    );
    const competencesComportementales = (candidat?.competences || []).filter(
        (c) => c.categorie !== 'Technique'
    );
    const langues = candidat?.langues || [];
    const certifications = candidat?.certifications || [];
    const projets = candidat?.projets || [];
    const centresInteret = candidat?.centres_interet || [];


    return (

        <div className="result-page">

            <Navbar activeStep={2} />


            <main className="result-content">

                {/*navigation*/}
                <div className="result-navigation">

                    <div className="result-tabs">

                        {sections.map((section, index) => (

                            <button
                                key={section.label}
                                className={`result-tab ${
                                    activeSection === index
                                        ? 'active'
                                        : ''
                                }`}
                                onClick={() => goToSection(index)}
                            >

                                <span className="result-tab-icon">
                                    {section.icon}
                                </span>

                                <span>
                                    {section.label}
                                </span>

                            </button>

                        ))}

                    </div>

                </div>

                <div className="result-indicator">

                    {sections.map((_, index) => (

                        <span
                            key={index}
                            className={
                                activeSection === index
                                    ? 'active'
                                    : ''
                            }
                        />

                    ))}

                </div>


                {/*contenu*/}

                <section className="result-card" key={candidat?.id || 'vide'}>


                    {/*candidat */}

                    {activeSection === 0 && (

                        <div className="result-section">

                            <div className="section-header">

                                <div className="section-header-icon">
                                    <PersonOutlineOutlinedIcon />
                                </div>

                                <div>
                                    <h2>
                                        Informations personnelles
                                    </h2>

                                    <p>
                                        Informations personnelles
                                        extraites du CV.
                                    </p>
                                </div>

                            </div>

                            <div className="form-grid">

                                <Champ label="Nom complet" value={candidat?.nom_complet} />
                                <Champ label="Titre du profil" value={candidat?.titre_profil} />
                                <Champ label="Email" value={candidat?.email} />
                                <Champ label="Téléphone" value={candidat?.telephone} />
                                <Champ label="Téléphone secondaire" value={candidat?.telephone_secondaire} />
                                <Champ label="Ville" value={candidat?.ville} />
                                <Champ label="Code postal" value={candidat?.code_postal} />
                                <Champ label="Pays" value={candidat?.pays} />
                                <Champ label="Adresse" value={candidat?.adresse} />
                                <Champ label="LinkedIn" value={candidat?.linkedin} />
                                <Champ label="Portfolio" value={candidat?.portfolio} />
                                <Champ label="Site web" value={candidat?.site_web} />
                                <Champ label="Date de naissance" value={candidat?.date_naissance} />
                                <Champ label="Lieu de naissance" value={candidat?.lieu_naissance} />
                                <Champ label="Nationalité" value={candidat?.nationalite} />
                                <Champ label="Situation familiale" value={candidat?.situation_familiale} />
                                <Champ label="Permis de conduire" value={candidat?.permis_conduire} />
                                <Champ label="Mobilité géographique" value={candidat?.mobilite_geographique} />
                                <Champ label="Disponibilité" value={candidat?.disponibilite} />
                                <Champ label="Résumé du profil" value={candidat?.resume_profil} />
                                <Champ label="Objectif professionnel" value={candidat?.objectif_professionnel} />

                            </div>

                        </div>

                    )}


                    {/*formations */}

                    {activeSection === 1 && (

                        <div className="result-section">

                            <div className="section-header">

                                <div className="section-header-icon">
                                    <SchoolOutlinedIcon />
                                </div>

                                <div>
                                    <h2>
                                        Formations
                                    </h2>

                                    <p>
                                        Parcours académique du candidat.
                                    </p>
                                </div>

                            </div>


                            <div className="items-container">

                                {formations.length === 0 && (
                                    <p>Aucune formation détectée pour ce CV.</p>
                                )}

                                {formations.map((formation, index) => (

                                    <article className="data-item" key={formation.id || index}>

                                        <div className="data-item-header">

                                            <div>
                                                <h3>
                                                    {formation.diplome || 'Diplôme non précisé'}
                                                </h3>

                                                <span>
                                                    {formation.etablissement || ''}
                                                </span>
                                            </div>

                                        </div>


                                        <div className="form-grid">

                                            <Champ label="Diplôme" value={formation.diplome} />
                                            <Champ label="Spécialité" value={formation.specialite} />
                                            <Champ label="Établissement" value={formation.etablissement} />
                                            <Champ label="Lieu" value={formation.lieu} />
                                            <Champ label="Date début" value={formation.date_debut} />
                                            <Champ label="Date fin" value={formation.date_fin} />
                                            <Champ label="Niveau" value={formation.niveau} />
                                            <Champ label="Mention" value={formation.mention} />
                                            <Champ label="Description" value={formation.description} />

                                        </div>

                                    </article>

                                ))}

                            </div>

                        </div>

                    )}


                    {/*experience*/}

                    {activeSection === 2 && (

                        <div className="result-section">

                            <div className="section-header">

                                <div className="section-header-icon">
                                    <WorkOutlineOutlinedIcon />
                                </div>

                                <div>
                                    <h2>
                                        Expériences professionnelles
                                    </h2>

                                    <p>
                                        Parcours professionnel extrait du CV.
                                    </p>
                                </div>

                            </div>


                            <div className="items-container">

                                {experiences.length === 0 && (
                                    <p>Aucune expérience détectée pour ce CV.</p>
                                )}

                                {experiences.map((experience, index) => (

                                    <article className="data-item" key={experience.id || index}>

                                        <div className="data-item-header">

                                            <div>
                                                <h3>
                                                    {experience.poste || 'Poste non précisé'}
                                                </h3>

                                                <span>
                                                    {experience.organisme || ''}
                                                </span>
                                            </div>

                                        </div>


                                        <div className="form-grid">

                                            <Champ label="Poste" value={experience.poste} />
                                            <Champ label="Type" value={experience.type} />
                                            <Champ label="Organisme" value={experience.organisme} />
                                            <Champ label="Lieu" value={experience.lieu} />
                                            <Champ label="Date début" value={experience.date_debut} />
                                            <Champ label="Date fin" value={experience.date_fin} />
                                            <Champ label="Description" value={experience.description} />

                                        </div>

                                    </article>

                                ))}

                            </div>

                        </div>

                    )}


                    {/*compétences */}

                    {activeSection === 3 && (

                        <div className="result-section">

                            <div className="section-header">

                                <div className="section-header-icon">
                                    <CodeOutlinedIcon />
                                </div>

                                <div>
                                    <h2>
                                        Compétences
                                    </h2>

                                    <p>
                                        Compétences techniques et
                                        comportementales.
                                    </p>
                                </div>

                            </div>


                            <div className="skills-block">

                                <h3>
                                    Compétences techniques
                                </h3>

                                <div className="skills-list">

                                    {competencesTechniques.length === 0 && (
                                        <p>Aucune compétence technique détectée.</p>
                                    )}

                                    {competencesTechniques.map((competence, index) => (
                                        <div className="skill-chip" key={competence.id || index}>
                                            <span>{competence.nom_competence}</span>
                                            <small>{competence.niveau || ''}</small>
                                        </div>
                                    ))}

                                </div>

                            </div>


                            <div className="skills-block">

                                <h3>
                                    Compétences comportementales
                                </h3>

                                <div className="skills-list">

                                    {competencesComportementales.length === 0 && (
                                        <p>Aucune compétence comportementale détectée.</p>
                                    )}

                                    {competencesComportementales.map((competence, index) => (
                                        <div className="skill-chip" key={competence.id || index}>
                                            <span>{competence.nom_competence}</span>
                                            <small>{competence.niveau || ''}</small>
                                        </div>
                                    ))}

                                </div>

                            </div>

                        </div>

                    )}


                    {/*langues */}

                    {activeSection === 4 && (

                        <div className="result-section">

                            <div className="section-header">

                                <div className="section-header-icon">
                                    <LanguageOutlinedIcon />
                                </div>

                                <div>
                                    <h2>
                                        Langues
                                    </h2>

                                    <p>
                                        Langues maîtrisées par le candidat.
                                    </p>
                                </div>

                            </div>


                            <div className="language-list">

                                {langues.length === 0 && (
                                    <p>Aucune langue détectée pour ce CV.</p>
                                )}

                                {langues.map((langue, index) => (

                                    <div className="language-item" key={langue.id || index}>
                                        <span>{langue.langue || '—'}</span>
                                        <span>{langue.niveau || '—'}</span>
                                    </div>

                                ))}

                            </div>

                        </div>

                    )}


                    {/*certifications */}

                    {activeSection === 5 && (

                        <div className="result-section">

                            <div className="section-header">

                                <div className="section-header-icon">
                                    <WorkspacePremiumOutlinedIcon />
                                </div>

                                <div>
                                    <h2>
                                        Certifications
                                    </h2>

                                    <p>
                                        Certifications obtenues par le candidat.
                                    </p>
                                </div>

                            </div>


                            <div className="items-container">

                                {certifications.length === 0 && (
                                    <p>Aucune certification détectée pour ce CV.</p>
                                )}

                                {certifications.map((certification, index) => (

                                    <article className="data-item" key={certification.id || index}>

                                        <div className="data-item-header">

                                            <h3>
                                                {certification.nom || 'Certification'}
                                            </h3>

                                        </div>


                                        <div className="form-grid">

                                            <Champ label="Nom" value={certification.nom} />
                                            <Champ label="Organisme" value={certification.organisme} />
                                            <Champ label="Date d'obtention" value={certification.date_obtention} />
                                            <Champ label="Date d'expiration" value={certification.date_expiration} />
                                            <Champ label="URL de vérification" value={certification.url_verification} />

                                        </div>

                                    </article>

                                ))}

                            </div>

                        </div>

                    )}


                    {/*projets */}

                    {activeSection === 6 && (

                        <div className="result-section">

                            <div className="section-header">

                                <div className="section-header-icon">
                                    <FolderOutlinedIcon />
                                </div>

                                <div>
                                    <h2>
                                        Projets
                                    </h2>

                                    <p>
                                        Projets personnels, académiques
                                        ou professionnels.
                                    </p>
                                </div>

                            </div>


                            <div className="items-container">

                                {projets.length === 0 && (
                                    <p>Aucun projet détecté pour ce CV.</p>
                                )}

                                {projets.map((projet, index) => (

                                    <article className="data-item" key={projet.id || index}>

                                        <div className="data-item-header">

                                            <h3>
                                                {projet.nom_projet || 'Projet'}
                                            </h3>

                                        </div>


                                        <div className="form-grid">

                                            <Champ label="Nom du projet" value={projet.nom_projet} />
                                            <Champ label="Type" value={projet.type_projet} />
                                            <Champ label="Rôle" value={projet.role} />
                                            <Champ label="Période" value={projet.periode} />
                                            <Champ label="Technologies" value={projet.technologies} />
                                            <Champ label="URL du projet" value={projet.url_projet} />
                                            <Champ label="Description" value={projet.description} />

                                        </div>

                                    </article>

                                ))}

                            </div>

                        </div>

                    )}


                    {/*centre d'intéret */}

                    {activeSection === 7 && (

                        <div className="result-section">

                            <div className="section-header">

                                <div className="section-header-icon">
                                    <InterestsOutlinedIcon />
                                </div>

                                <div>
                                    <h2>
                                        Centres d'intérêt
                                    </h2>

                                    <p>
                                        Centres d'intérêt personnels
                                        du candidat.
                                    </p>
                                </div>

                            </div>


                            <div className="interest-list">

                                {centresInteret.length === 0 && (
                                    <p>Aucun centre d'intérêt détecté pour ce CV.</p>
                                )}

                                {centresInteret.map((interet, index) => (

                                    <div className="interest-item" key={interet.id || index}>
                                        <span>{interet.intitule || '—'}</span>
                                        <span>{interet.categorie || '—'}</span>
                                    </div>

                                ))}

                            </div>

                        </div>

                    )}

                </section>


                {/*navigation entre sections */}

                <div className="result-actions" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '25px', gap: '15px' }}>

                    <button
                        className="secondary-button"
                        onClick={() => goToSection(activeSection - 1)}
                        disabled={activeSection === 0}
                    >
                        ← Précédent
                    </button>

                    <button
                        type="button"
                        className="primary-button"
                        onClick={handleNouveauCV}
                        style={{ backgroundColor: '#00843d', padding: '12px 24px', fontWeight: '700', borderRadius: '8px' }}
                    >
                        ➕ Analyser un autre CV
                    </button>

                    <button
                        className="primary-button"
                        onClick={() => goToSection(activeSection + 1)}
                        disabled={activeSection === sections.length - 1}
                    >
                        Suivant →
                    </button>

                </div>

            </main>

        </div>
    );
}

export default Result;
