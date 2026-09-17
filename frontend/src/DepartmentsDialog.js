import React, { useEffect, useMemo, useState } from "react";
import {
    Alert,
    Box,
    Button,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    InputAdornment,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography,
} from "@mui/material";
import BusinessIcon from "@mui/icons-material/Business";
import SearchIcon from "@mui/icons-material/Search";
import { getDepartments } from "./data/Course";

const headerSx = {
    display: "flex",
    alignItems: "center",
    gap: 1.5,
    padding: (theme) => theme.spacing(2, 3),
    borderBottom: "1px solid var(--border)",
};

// The list runs to a couple of hundred rows. Only the table scrolls, so the
// search box stays put above it and Table's own sticky header has a scrolling
// ancestor to stick to.
const bodySx = {
    padding: 0,
    overflowY: "hidden",
    display: "flex",
    flexDirection: "column",
    minHeight: 0,
};

const searchSx = {
    padding: (theme) => theme.spacing(2, 3, 1.5, 3),
    flexShrink: 0,
};

const cellSx = {
    backgroundColor: "background.paper",
    fontWeight: 600,
};

const normalise = (text) => text.toLocaleUpperCase("tr");

export default function DepartmentsDialog({ open, onClose }) {
    const [departments, setDepartments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [failed, setFailed] = useState(false);
    const [query, setQuery] = useState("");

    useEffect(() => {
        if (!open) return;

        setLoading(true);
        setFailed(false);
        getDepartments()
            .then(setDepartments)
            .catch(() => setFailed(true))
            .finally(() => setLoading(false));
    }, [open]);

    const visibleDepartments = useMemo(() => {
        const needle = normalise(query.trim());

        if (!needle) return departments;

        return departments.filter(
            (department) =>
                normalise(department.abbreviation).includes(needle) ||
                normalise(department.name).includes(needle)
        );
    }, [departments, query]);

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="sm"
            fullWidth
            PaperProps={{ sx: { borderRadius: "16px", maxHeight: "90vh" } }}
        >
            <Box sx={headerSx}>
                <BusinessIcon color="primary" />
                <Box>
                    <Typography variant="h6">Departments</Typography>
                    <Typography variant="body2" color="text.secondary">
                        The abbreviation to type in the Department field.
                    </Typography>
                </Box>
            </Box>

            <DialogContent sx={bodySx}>
                {loading && (
                    <Box sx={{ display: "flex", justifyContent: "center", padding: 4 }}>
                        <CircularProgress />
                    </Box>
                )}

                {!loading && failed && (
                    <Box sx={{ padding: 3 }}>
                        <Alert severity="error">
                            Course data could not be loaded, so the department list is
                            unavailable.
                        </Alert>
                    </Box>
                )}

                {!loading && !failed && (
                    <>
                        <Box sx={searchSx}>
                            <TextField
                                fullWidth
                                size="small"
                                autoFocus
                                value={query}
                                placeholder="e.g. CENG or Computer"
                                onChange={(event) => setQuery(event.target.value)}
                                InputProps={{
                                    startAdornment: (
                                        <InputAdornment position="start">
                                            <SearchIcon fontSize="small" />
                                        </InputAdornment>
                                    ),
                                }}
                            />
                        </Box>

                        {visibleDepartments.length === 0 ? (
                            <Box sx={{ padding: 3, flexShrink: 0 }}>
                                <Alert severity="info">
                                    No department matches "{query.trim()}".
                                </Alert>
                            </Box>
                        ) : (
                            <TableContainer sx={{ flex: 1, overflowY: "auto" }}>
                                <Table size="small" stickyHeader>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell sx={{ ...cellSx, width: "6.5rem" }}>
                                                Abbreviation
                                            </TableCell>
                                            <TableCell sx={cellSx}>Department</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {visibleDepartments.map((department) => (
                                            <TableRow key={department.abbreviation} hover>
                                                <TableCell sx={{ fontWeight: 600 }}>
                                                    {department.abbreviation}
                                                </TableCell>
                                                <TableCell>{department.name}</TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        )}
                    </>
                )}
            </DialogContent>

            <DialogActions sx={{ padding: (theme) => theme.spacing(1.5, 3) }}>
                <Typography variant="body2" color="text.secondary" sx={{ marginRight: "auto" }}>
                    {visibleDepartments.length} of {departments.length} departments
                </Typography>
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
}
