package com.jonasfh.picobelltaco.ui

import android.view.*
import androidx.fragment.app.Fragment
import com.jonasfh.picobelltaco.R

/**
 * Interface som fragments implementerer når de ønsker meny.
 */
interface HasMenu {
    fun onMenuSelected(item: MenuItem): Boolean
}

/**
 * Hjelpeklasse for enkelt oppsett av en meny i fragments.
 */
object MainMenu {
    fun setup(fragment: Fragment) {
        fragment.setHasOptionsMenu(true)
    }

    fun inflate(menu: Menu, inflater: MenuInflater) {
        menu.clear()
        inflater.inflate(R.menu.main_menu, menu)
    }
}