import { describe, expect, it } from 'vitest'
import { aktiveSpieler, gegenspielerNamen, geberFuerRunde } from './rotation'

const spieler = ['Anna', 'Bernd', 'Carla', 'Dirk']

describe('geberFuerRunde', () => {
  it('startet in Runde 1 beim ersten Spieler und rotiert streng reihum', () => {
    expect(geberFuerRunde(spieler, 1)).toBe('Anna')
    expect(geberFuerRunde(spieler, 2)).toBe('Bernd')
    expect(geberFuerRunde(spieler, 3)).toBe('Carla')
    expect(geberFuerRunde(spieler, 4)).toBe('Dirk')
  })

  it('beginnt nach einem vollen Durchgang wieder von vorne', () => {
    expect(geberFuerRunde(spieler, 5)).toBe('Anna')
    expect(geberFuerRunde(spieler, 8)).toBe('Dirk')
    expect(geberFuerRunde(spieler, 12)).toBe('Dirk')
  })
})

describe('aktiveSpieler', () => {
  it('liefert die drei Spieler ohne den aussetzenden Geber', () => {
    expect(aktiveSpieler(spieler, 'Anna')).toEqual(['Bernd', 'Carla', 'Dirk'])
    expect(aktiveSpieler(spieler, 'Carla')).toEqual(['Anna', 'Bernd', 'Dirk'])
  })
})

describe('gegenspielerNamen', () => {
  it('liefert die aktiven Spieler ohne den Spielmacher', () => {
    const aktive = aktiveSpieler(spieler, 'Anna')
    expect(gegenspielerNamen(aktive, 'Bernd')).toEqual(['Carla', 'Dirk'])
  })
})
