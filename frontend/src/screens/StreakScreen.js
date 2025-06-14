import React from 'react';
import { View, Text, Button } from 'react-native';

export default function StreakScreen({ navigation }) {
  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text>Streak Screen</Text>
      <Button title="Go Home" onPress={() => navigation.navigate('Home')} />
    </View>
  );
}
