import './FileCard.css';

import InsertDriveFileOutlinedIcon from '@mui/icons-material/InsertDriveFileOutlined';
import CloseIcon from '@mui/icons-material/Close';

function FileCard({ file, onRemove }) {
    return (
        <div className="file-card">

            <div className="file-info">

                <InsertDriveFileOutlinedIcon className="file-icon" />

                <span className="file-name">
                    {file.name}
                </span>

            </div>

            <button
                className="remove-file"
                type="button"
                onClick={onRemove}
                aria-label="Supprimer le fichier"
            >
                <CloseIcon />
            </button>

        </div>
    );
}

export default FileCard;