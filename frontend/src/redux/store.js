import { configureStore } from '@reduxjs/toolkit';
import candidateReducer from './candidateSlice';

export const store = configureStore({
    reducer: {
        candidate: candidateReducer,
    },
});