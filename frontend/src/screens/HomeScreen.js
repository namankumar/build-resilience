import React from 'react';
import { View, Text, Button } from 'react-native';

export default function HomeScreen({ navigation }) {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Home Screen</Text>
      <Button title="What's going on right now?" onPress={() => navigation.navigate('Reflect')} />
      <Button title="My Streak" onPress={() => navigation.navigate('Streak')} />
      <Button title="My Wins" onPress={() => navigation.navigate('WinRack')} />
    </View>
  );
}
