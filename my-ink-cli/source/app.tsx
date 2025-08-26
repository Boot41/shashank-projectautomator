import React from "react";
import { Text } from "ink";

export default function App({ name = "World" }: { name?: string }) {
	return <Text>Hello, {name}</Text>;
}
