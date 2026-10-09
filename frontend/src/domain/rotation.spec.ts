import { describe, expect, it } from 'vitest'
import { aktiveSpieler, gegenspielerNamen, geberFuerRunde, geberSetztAus } from './rotation'

/** Beide unterstützten Varianten (ADR-017): Spielerreihenfolge je Spielerzahl. */
const VARIANTEN = [
  { name: '4 Spieler', spieler: ['Anna', 'Bernd', 'Carla', 'Dirk'] },
  { name: '3 Spieler', spieler: ['Anna', 'Bernd', 'Carla'] },
] as const

describe.each(VARIANTEN)('Rotation und Rollen bei $name', ({ spieler }) => {
  const n = spieler.length

  it('startet in Runde 1 beim ersten Spieler und rotiert streng reihum', () => {
    for (let runde = 1; runde <= n; runde++) {
      expect(geberFuerRunde([...spieler], runde)).toBe(spieler[runde - 1])
    }
  })

  it('beginnt nach einem vollen Durchgang wieder von vorne', () => {
    expect(geberFuerRunde([...spieler], n + 1)).toBe(spieler[0])
    expect(geberFuerRunde([...spieler], 2 * n)).toBe(spieler[n - 1])
    expect(geberFuerRunde([...spieler], 12)).toBe(spieler[(12 - 1) % n])
  })

  it('lässt in jeder Runde genau drei Spieler aktiv mitspielen', () => {
    for (const geber of spieler) {
      expect(aktiveSpieler([...spieler], geber)).toHaveLength(3)
    }
  })

  it('liefert für jeden Spielmacher genau zwei Gegenspieler', () => {
    for (const geber of spieler) {
      const aktive = aktiveSpieler([...spieler], geber)
      for (const spielmacher of aktive) {
        const gegenspieler = gegenspielerNamen(aktive, spielmacher)
        expect(gegenspieler).toHaveLength(2)
        expect(gegenspieler).not.toContain(spielmacher)
      }
    }
  })
})

describe('geberSetztAus', () => {
  it('ist nur bei vier Spielern wahr', () => {
    expect(geberSetztAus(['Anna', 'Bernd', 'Carla', 'Dirk'])).toBe(true)
    expect(geberSetztAus(['Anna', 'Bernd', 'Carla'])).toBe(false)
  })
})

describe('aktiveSpieler', () => {
  it('bei 4 Spielern: alle außer dem aussetzenden Geber', () => {
    const spieler = ['Anna', 'Bernd', 'Carla', 'Dirk']
    expect(aktiveSpieler(spieler, 'Anna')).toEqual(['Bernd', 'Carla', 'Dirk'])
    expect(aktiveSpieler(spieler, 'Carla')).toEqual(['Anna', 'Bernd', 'Dirk'])
  })

  it('bei 3 Spielern: alle drei – der Geber spielt mit', () => {
    const spieler = ['Anna', 'Bernd', 'Carla']
    for (const geber of spieler) {
      expect(aktiveSpieler(spieler, geber)).toEqual(['Anna', 'Bernd', 'Carla'])
    }
  })
})

describe('gegenspielerNamen', () => {
  it('bei 4 Spielern: aktive ohne Spielmacher', () => {
    const aktive = aktiveSpieler(['Anna', 'Bernd', 'Carla', 'Dirk'], 'Anna')
    expect(gegenspielerNamen(aktive, 'Bernd')).toEqual(['Carla', 'Dirk'])
  })

  it('bei 3 Spielern kann der Geber Gegenspieler oder Spielmacher sein', () => {
    const spieler = ['Anna', 'Bernd', 'Carla']
    const aktive = aktiveSpieler(spieler, 'Anna')
    expect(gegenspielerNamen(aktive, 'Bernd')).toEqual(['Anna', 'Carla']) // Geber spielt mit
    expect(gegenspielerNamen(aktive, 'Anna')).toEqual(['Bernd', 'Carla']) // Geber ist Spielmacher
  })
})
