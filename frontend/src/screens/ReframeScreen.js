import React from 'react';
import { View, Text, Button } from 'react-native';

export default function ReframeScreen({ route, navigation }) {
  const { text } = route.params;
  const reframe = `Reframe for: ${text}`;
  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text>{reframe}</Text>
      <Button title="Take a small step" onPress={() => navigation.navigate('Win')} />
    </View>
  );
}
