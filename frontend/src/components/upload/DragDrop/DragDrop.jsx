import { useState } from 'react';
import './DragDrop.css';

function DragDrop({ children, onFileSelect }) {
    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = (event) => {
        event.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (event) => {
        event.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (event) => {
        event.preventDefault();
        setIsDragging(false);

        const file = event.dataTransfer.files[0];

        if (file && onFileSelect) {
            onFileSelect(file);
        }
    };

    return (
        <div
            className={`drag-drop-wrapper ${
                isDragging ? 'dragging' : ''
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            {children}
        </div>
    );
}

export default DragDrop;