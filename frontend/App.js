import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from './src/screens/HomeScreen';
import ReflectionInputScreen from './src/screens/ReflectionInputScreen';
import ReframeScreen from './src/screens/ReframeScreen';
import WinScreen from './src/screens/WinScreen';
import StreakScreen from './src/screens/StreakScreen';
import WinRackScreen from './src/screens/WinRackScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Reflect" component={ReflectionInputScreen} />
        <Stack.Screen name="Reframe" component={ReframeScreen} />
        <Stack.Screen name="Win" component={WinScreen} />
        <Stack.Screen name="Streak" component={StreakScreen} />
        <Stack.Screen name="WinRack" component={WinRackScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
