<?php

declare(strict_types=1);

use Phinx\Migration\AbstractMigration;

final class DoorbellEventsTable extends AbstractMigration
{
    /**
     * Change Method.
     *
     * Write your reversible migrations using this method.
     *
     * More information on writing migrations is available here:
     * https://book.cakephp.org/phinx/0/en/migrations.html#the-change-method
     *
     * Remember to call "create()" or "update()" and NOT "save()" when working
     * with the Table class.
     */
    public function change(): void
    {
        // === DOORBELL EVENTS ===
        $this->table('doorbell_events')
            ->addColumn('pico_serial', 'string', [
                'limit' => 255,
                'null' => false,
            ])
            ->addColumn('created_at', 'datetime', [
                'default' => 'CURRENT_TIMESTAMP',
            ])
            ->addColumn('open_requested', 'boolean', [
                'default' => false,
            ])
            ->addColumn('opened_at', 'datetime', [
                'null' => true,
                'default' => null,
            ])
            ->create();
    }
}
