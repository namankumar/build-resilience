import React from 'react';
import { View, Text, Button } from 'react-native';

export default function WinScreen({ navigation }) {
  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text>Choose a micro-win</Text>
      <Button title="I did this" onPress={() => navigation.navigate('Streak')} />
    </View>
  );
}
