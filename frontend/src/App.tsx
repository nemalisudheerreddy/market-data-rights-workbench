import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

const API_URL = import.meta.env.VITE_API_URL;

type DocumentRecord = {
  id: number;
  filename: string;
  file_type: string;
};

export default function App() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadDocuments() {
    const response = await fetch(`${API_URL}/api/documents`);
    const data = await response.json();
    setDocuments(data);
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function uploadFile(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];

    if (!file) return;

    setLoading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_URL}/api/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setMessage(
        data.duplicate
          ? "Duplicate document detected."
          : "Document processed successfully."
      );

      await loadDocuments();
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : "Upload failed."
      );
    } finally {
      setLoading(false);
      event.target.value = "";
    }
  }

  async function askQuestion() {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/api/ask`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question}),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Question failed.");
      }

      setAnswer(data.answer);
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : "Question failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box sx={{minHeight: "100vh", bgcolor: "#f4f7fb", py: 5}}>
      <Container maxWidth="lg">
        <Stack spacing={3}>
          <Box>
            <Typography variant="h3" fontWeight={700}>
              Market Data Rights Workbench
            </Typography>

            <Typography color="text.secondary">
              Contract, feed, entitlement and rights analysis
            </Typography>
          </Box>

          {message && <Alert severity="info">{message}</Alert>}

          <Paper sx={{p: 3}}>
            <Typography variant="h5" gutterBottom>
              Corpus ingestion
            </Typography>

            <Button variant="contained" component="label">
              Upload document
              <input
                hidden
                type="file"
                accept=".pdf,.docx,.csv,.xlsx,.json,.txt,.md"
                onChange={uploadFile}
              />
            </Button>

            <Typography sx={{mt: 2}}>
              {documents.length} document(s) processed
            </Typography>

            {documents.map((document) => (
              <Typography key={document.id} variant="body2">
                {document.filename} — {document.file_type}
              </Typography>
            ))}
          </Paper>

          <Paper sx={{p: 3}}>
            <Typography variant="h5" gutterBottom>
              Natural-language contract analysis
            </Typography>

            <TextField
              fullWidth
              multiline
              minRows={3}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Can this feed be used for external redistribution?"
            />

            <Button
              sx={{mt: 2}}
              variant="contained"
              disabled={loading}
              onClick={askQuestion}
            >
              Analyze
            </Button>

            {loading && (
              <CircularProgress size={24} sx={{ml: 2}} />
            )}

            {answer && (
              <Paper variant="outlined" sx={{p: 2, mt: 3}}>
                <Typography whiteSpace="pre-wrap">
                  {answer}
                </Typography>
              </Paper>
            )}
          </Paper>
        </Stack>
      </Container>
    </Box>
  );
}