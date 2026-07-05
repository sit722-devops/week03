import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import App from "./App";

describe("Campus Course Platform Frontend", () => {
    beforeEach(() => {
        global.fetch = vi.fn((url) => {
            if (url.includes("/students")) {
                return Promise.resolve({
                    json: () => Promise.resolve([])
                });
            }

            if (url.includes("/courses")) {
                return Promise.resolve({
                    json: () => Promise.resolve([])
                });
            }

            return Promise.resolve({
                json: () => Promise.resolve([])
            });
        });
    });

    test("renders main page title", async () => {
        render(<App />);

        expect(
            screen.getByText("Campus Course Platform")
        ).toBeInTheDocument();
    });

    test("renders student form", async () => {
        render(<App />);

        expect(screen.getByRole("heading", { name: "Add Student" })).toBeInTheDocument();        expect(screen.getByPlaceholderText("Student ID")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Name")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Program")).toBeInTheDocument();
    });

    test("renders course form", async () => {
        render(<App />);

        expect(screen.getByRole("heading", { name: "Add Course" })).toBeInTheDocument();        expect(screen.getByPlaceholderText("Course ID")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Course Name")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Credit Points")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Faculty")).toBeInTheDocument();
    });

    test("shows no student data message when students list is empty", async () => {
        render(<App />);

        await waitFor(() => {
            expect(screen.getByText("No student data found.")).toBeInTheDocument();
        });
    });

    test("shows no course data message when courses list is empty", async () => {
        render(<App />);

        await waitFor(() => {
            expect(screen.getByText("No course data found.")).toBeInTheDocument();
        });
    });
});