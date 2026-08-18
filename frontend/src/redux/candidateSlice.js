import { createSlice, createAsyncThunk } from "@reduxjs/toolkit"
import api from "../services/api"

// THUNK → récupérer résultat OCR
export const fetchResult = createAsyncThunk(
  "candidate/fetchResult",
  async (candidatId, thunkAPI) => {
    try {
      const response = await api.get(`/candidats/${candidatId}/`)
      return response.data
    } catch (error) {
      return thunkAPI.rejectWithValue(error.response?.data || error.message)
    }
  }
)

// SLICE
const candidateSlice = createSlice({
  name: "candidate",
  initialState: {
    candidatId: null,
    statutTraitement: null,
    nomFichier: null,
    data: null,
    loading: false,
    error: null,
  },
  reducers: {
    setCandidat: (state, action) => {
      state.candidatId = action.payload.id
      state.statutTraitement = action.payload.statut_traitement
      state.nomFichier = action.payload.nomFichier || action.payload.fichier_cv
    },
    resetCandidat: (state) => {
      state.candidatId = null
      state.statutTraitement = null
      state.nomFichier = null
      state.data = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchResult.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchResult.fulfilled, (state, action) => {
        state.loading = false
        state.data = action.payload
      })
      .addCase(fetchResult.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
  },
})

export const { setCandidat, resetCandidat } = candidateSlice.actions
export default candidateSlice.reducer