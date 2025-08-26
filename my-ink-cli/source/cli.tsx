#!/usr/bin/env node
import React from "react";
import { render } from "ink";
import App from "./app.js"; // note the `.js` because TSX compiles to JS

// Read CLI args (skip first 2 default ones: node + script path)
const [,, ...args] = process.argv;

render(<App name={args[0] || "World"} />);
