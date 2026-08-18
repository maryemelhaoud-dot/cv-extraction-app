import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import './UploadZone.css';

import DragDrop from '../DragDrop/DragDrop';
import FileCard from '../FileCard/FileCard';
import { setCandidat } from '../../../redux/candidateSlice';
import { uploadCV } from '../../../services/uploadService';

import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined';
import FolderOutlinedIcon from '@mui/icons-material/FolderOutlined';

function UploadZone() {

    const [selectedFile, setSelectedFile] = useState(null);
    const [provider, setProvider] = useState('gemini_direct');
    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState(null);

    const dispatch = useDispatch();
    const navigate = useNavigate();

    const handleFileSelect = (file) => {
        setSelectedFile(file);
        setUploadError(null);
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];

        if (file) {
            setSelectedFile(file);
            setUploadError(null);
        }
    };

    const handleRemoveFile = () => {
        setSelectedFile(null);
        setUploadError(null);
    };

    const handleAnalyser = async () => {
        if (!selectedFile) return;

        setIsUploading(true);
        setUploadError(null);

        try {
            const resultat = await uploadCV(selectedFile, provider);
            dispatch(setCandidat(resultat));
            navigate('/extraction');
        } catch (erreur) {
            console.error("Erreur lors de l'upload :", erreur);
            setUploadError("L'envoi du fichier a échoué. Réessayez.");
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <DragDrop onFileSelect={handleFileSelect}>

            <div className="upload-zone">

                {/* Icône upload */}
                <div className="upload-icon">
                    <CloudUploadOutlinedIcon />
                </div>

                <h3>
                    Glissez-déposez votre CV ici
                </h3>

                <p>
                    ou cliquez pour parcourir
                </p>

                {/* Input fichier caché */}
                <input
                    type="file"
                    id="file-upload"
                    className="file-input"
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={handleFileChange}
                />

                {/* Bouton parcourir */}
                <label
                    htmlFor="file-upload"
                    className="upload-button"
                >
                    <FolderOutlinedIcon />
                    <span>Parcourir les fichiers</span>
                </label>

                {/* Choix de la méthode d'extraction */}
                <div className="provider-selector" style={{ margin: '18px 0 10px', width: '100%', maxWidth: '400px' }}>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#102a43', marginBottom: '6px', textAlign: 'center' }}>
                        Méthode d'extraction :
                    </label>
                    <select
                        value={provider}
                        onChange={(e) => setProvider(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '10px 14px',
                            borderRadius: '8px',
                            border: '1px solid #00843d',
                            backgroundColor: '#ffffff',
                            color: '#102a43',
                            fontSize: '14px',
                            fontWeight: '500',
                            cursor: 'pointer',
                            boxShadow: '0 2px 6px rgba(0,0,0,0.06)'
                        }}
                    >
                        <option value="gemini_direct">Gemini Vision Direct (IA Cloud)</option>
                        <option value="paddle_groq">PaddleOCR + Groq Llama 3 (Gratuit)</option>
                        <option value="paddle_gemini">PaddleOCR + Gemini (Texte OCR pur transmis à Gemini)</option>
                        <option value="paddle_deepseek">PaddleOCR + DeepSeek (Texte OCR pur + LLM Payant)</option>
                    </select>
                </div>

                {/* Fichier sélectionné */}
                {selectedFile && (
                    <FileCard
                        file={selectedFile}
                        onRemove={handleRemoveFile}
                    />
                )}

                {/* Bouton Analyser, visible seulement si un fichier est choisi */}
                {selectedFile && (
                    <button
                        type="button"
                        className="upload-button analyser-button"
                        onClick={handleAnalyser}
                        disabled={isUploading}
                    >
                        <span>{isUploading ? 'Envoi en cours...' : 'Analyser'}</span>
                    </button>
                )}

                {/* Message d'erreur */}
                {uploadError && (
                    <p className="upload-error">{uploadError}</p>
                )}

            </div>

        </DragDrop>
    );
}

export default UploadZone;