// Testing utilities from React Testing Library
import { render, screen, waitFor } from "@testing-library/react";
// act helper to wrap updates that can cause side effects
import { act } from "react-dom/test-utils";
// vitest testing functions and mocking utility
import { describe, expect, test, vi } from "vitest";
// Component under test
import App from "./App";

describe("Campus Course Platform Frontend", () => {
    // Mock global fetch to return empty lists for students and courses
    beforeEach(() => {
        global.fetch = vi.fn((url) => {
            if (url.includes("/students")) {
                return Promise.resolve({ json: () => Promise.resolve([]) });
            }

            if (url.includes("/courses")) {
                return Promise.resolve({ json: () => Promise.resolve([]) });
            }

            // default: return empty array
            return Promise.resolve({ json: () => Promise.resolve([]) });
        });
    });

    // Ensure the main title is displayed
    test("renders main page title", async () => {
        act(() => {
            render(<App />);
        });

        expect(screen.getByText("Campus Course Platform")).toBeInTheDocument();
    });

    // Check that the Add Student form and its fields render
    test("renders student form", async () => {
        act(() => {
            render(<App />);
        });

        expect(screen.getByRole("heading", { name: "Add Student" })).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Student ID")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Name")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Program")).toBeInTheDocument();
    });

    // Check that the Add Course form and its fields render
    test("renders course form", async () => {
        act(() => {
            render(<App />);
        });

        expect(screen.getByRole("heading", { name: "Add Course" })).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Course ID")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Course Name")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Credit Points")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Faculty")).toBeInTheDocument();
    });

    // When students API returns empty list, show appropriate message
    test("shows no student data message when students list is empty", async () => {
        act(() => {
            render(<App />);
        });

        await waitFor(() => {
            expect(screen.getByText("No student data found.")).toBeInTheDocument();
        });
    });

    // When courses API returns empty list, show appropriate message
    test("shows no course data message when courses list is empty", async () => {
        act(() => {
            render(<App />);
        });

        await waitFor(() => {
            expect(screen.getByText("No course data found.")).toBeInTheDocument();
        });
    });
});